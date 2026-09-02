package link.artof.aea.companion.data.repository

import link.artof.aea.companion.data.api.BffClient
import link.artof.aea.companion.data.model.AcceptedResponse
import link.artof.aea.companion.data.model.Arrangement
import link.artof.aea.companion.data.model.BffException
import link.artof.aea.companion.data.model.ChatMessage
import link.artof.aea.companion.data.model.CheckoutRequest
import link.artof.aea.companion.data.model.ConversationMessageDto
import link.artof.aea.companion.data.model.DeliveryDetails
import link.artof.aea.companion.data.model.DeliveryRequest
import link.artof.aea.companion.data.model.DeliveryTiming
import link.artof.aea.companion.data.model.OrderResult
import link.artof.aea.companion.data.model.SelectionRequest
import link.artof.aea.companion.data.model.SharedUnderstanding
import link.artof.aea.companion.data.model.SharedUnderstandingResponse
import link.artof.aea.companion.data.model.WorkspaceResponse
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.time.LocalDate
import java.util.UUID

enum class JourneyStage {
    NEED,
    PICK,
    PAY,
    TRACKING
}

/**
 * Live BFF-backed journey repository (internal testing).
 * Occasion unlock comes from GET shared-understanding after live messages — not Mom keywords (#357).
 */
class SessionRepository(
    private val api: BffClient = BffClient()
) {
    private val _currentStage = MutableStateFlow(JourneyStage.NEED)
    val currentStage: StateFlow<JourneyStage> = _currentStage.asStateFlow()

    private val _messages = MutableStateFlow(
        listOf(
            ChatMessage(
                id = "welcome",
                sender = "florist",
                text = "Welcome to Lily's Florist. Who are we celebrating today, and when do you need the delivery?"
            )
        )
    )
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()

    private val localFallbackCatalog = listOf(
        Arrangement(
            sku = "classic-rose-dozen",
            name = "Classic Rose Dozen",
            price = 70.00,
            description = "Reference catalog roses (local fallback when workspace catalog unavailable).",
            available = true,
            tags = listOf("Same-Day", "Best Seller")
        ),
        Arrangement(
            sku = "budget-mixed-bunch",
            name = "Budget Mixed Bunch",
            price = 35.00,
            description = "Value mixed bunch from reference catalog.",
            available = true,
            tags = listOf("Budget")
        ),
        Arrangement(
            sku = "lilac-bouquet",
            name = "Lilac Bouquet",
            price = 95.00,
            description = "Seasonal lilac bouquet.",
            available = true,
            tags = listOf("Premium")
        ),
        Arrangement(
            sku = "peony-sold-out-local",
            name = "Blush Peonies (local fallback)",
            price = 85.00,
            description = "Sold-out fail-closed example when catalog is local fallback.",
            available = false,
            tags = listOf("Sold Out Today", "Pre-Order Only")
        )
    )

    private val _arrangements = MutableStateFlow(localFallbackCatalog)
    val arrangements: StateFlow<List<Arrangement>> = _arrangements.asStateFlow()

    private val _selectedArrangement = MutableStateFlow<Arrangement?>(null)
    val selectedArrangement: StateFlow<Arrangement?> = _selectedArrangement.asStateFlow()

    private val _sharedUnderstanding = MutableStateFlow(SharedUnderstanding())
    val sharedUnderstanding: StateFlow<SharedUnderstanding> = _sharedUnderstanding.asStateFlow()

    private val _orderResult = MutableStateFlow<OrderResult?>(null)
    val orderResult: StateFlow<OrderResult?> = _orderResult.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _sessionReady = MutableStateFlow(false)
    val sessionReady: StateFlow<Boolean> = _sessionReady.asStateFlow()

    /** Authoritative checkout total from workspace order_summary (product + delivery). */
    private val _orderSummaryTotal = MutableStateFlow<Double?>(null)
    val orderSummaryTotal: StateFlow<Double?> = _orderSummaryTotal.asStateFlow()

    private var contextVersion: Int = 0
    private var usingLocalCatalogFallback: Boolean = true

    suspend fun ensureSession() {
        if (_sessionReady.value) return
        runGuarded {
            api.createSession()
            _sessionReady.value = true
            refreshSharedUnderstanding()
        }
    }

    /**
     * Post user text to live conversation/messages, then refresh shared-understanding
     * and conversation. Does NOT keyword-match Mom/birthday for occasion unlock.
     */
    suspend fun postUserMessage(text: String) {
        val trimmed = text.trim()
        if (trimmed.isEmpty()) return
        runGuarded {
            ensureSessionInternal()
            val optimistic = ChatMessage(
                id = UUID.randomUUID().toString(),
                sender = "user",
                text = trimmed
            )
            _messages.value = _messages.value + optimistic

            val accepted: AcceptedResponse = postConversationRetryingStale(
                messageText = trimmed,
                observedContextVersion = contextVersion
            )
            if (accepted.contextVersion > 0) {
                contextVersion = accepted.contextVersion
            }
            refreshSharedUnderstanding()
            refreshConversation()
            refreshCatalogFromWorkspace()
        }
    }

    fun clearError() {
        _errorMessage.value = null
    }

    fun moveToPickStage() {
        _currentStage.value = JourneyStage.PICK
    }

    /**
     * Fail-closed locally if unavailable; otherwise POST /api/v1/selection to live BFF.
     */
    suspend fun selectArrangement(arrangement: Arrangement) {
        if (!arrangement.available) return // NFR-009 fail-closed
        runGuarded {
            ensureSessionInternal()
            val accepted = api.postSelection(
                SelectionRequest(
                    productId = arrangement.sku,
                    observedContextVersion = contextVersion
                )
            )
            if (accepted.contextVersion > 0) {
                contextVersion = accepted.contextVersion
            }
            _selectedArrangement.value = arrangement
            _sharedUnderstanding.value = _sharedUnderstanding.value.copy(selectedSku = arrangement.sku)
            refreshSharedUnderstanding()
        }
    }

    fun moveToPayStage() {
        _currentStage.value = JourneyStage.PAY
    }

    /** Pick → Need: clear local selection so Pick does not keep a stale card (#365). */
    fun backToNeed() {
        _selectedArrangement.value = null
        _sharedUnderstanding.value = _sharedUnderstanding.value.copy(selectedSku = null)
        _orderSummaryTotal.value = null
        _errorMessage.value = null
        _currentStage.value = JourneyStage.NEED
    }

    /** Pay → Pick (#365). */
    fun backToPick() {
        _errorMessage.value = null
        _currentStage.value = JourneyStage.PICK
    }

    /**
     * Display total for Pay: authoritative order_summary when known, else product +
     * reference delivery fee (mirrors platform REFERENCE_DELIVERY_FEE = 12.0).
     */
    fun displayCheckoutTotal(selectedPrice: Double?): Double {
        orderSummaryTotal.value?.let { return it }
        val product = selectedPrice ?: return 0.0
        return product + REFERENCE_DELIVERY_FEE
    }

    /**
     * Live checkout path: refresh context_version, optional card_message via selection,
     * delivery, POST /order, then POST /checkout with opaque session_pay_ref and
     * observed_total from workspace order_summary (not product-only — #365 total_mismatch).
     * One-shot stale_context retry on selection/delivery only (not product_unavailable).
     */
    suspend fun completeCheckout(cardMessage: String) {
        val selected = _selectedArrangement.value ?: return
        runGuarded {
            ensureSessionInternal()
            // Authoritative context_version before the mutation chain (#365).
            refreshContextFromWorkspace()

            val options = if (cardMessage.isNotBlank()) {
                mapOf("card_message" to cardMessage.take(280))
            } else {
                emptyMap()
            }
            val selectAccepted = postSelectionRetryingStale(
                SelectionRequest(
                    productId = selected.sku,
                    options = options,
                    observedContextVersion = contextVersion
                )
            )
            if (selectAccepted.contextVersion > 0) {
                contextVersion = selectAccepted.contextVersion
            }

            val today = LocalDate.now().toString()
            val deliveryAccepted = postDeliveryRetryingStale(
                DeliveryRequest(
                    delivery = DeliveryDetails(
                        timing = DeliveryTiming(date = today, window = "afternoon"),
                        destinationReference = BffClient.SESSION_DESTINATION_REFERENCE
                    ),
                    observedContextVersion = contextVersion
                )
            )
            if (deliveryAccepted.contextVersion > 0) {
                contextVersion = deliveryAccepted.contextVersion
            }

            // Mirror web confirmAndPay: observed_total = Number(order_summary.total).
            // Delivery fee is applied after postDelivery; product-only price → total_mismatch.
            val workspaceAfterDelivery = api.getWorkspace()
            adoptWorkspace(workspaceAfterDelivery)
            val summaryTotal = workspaceAfterDelivery.facets.orderSummary?.total

            val orderAccepted = api.postOrder()
            val workspaceAfterOrder = api.getWorkspace()
            adoptWorkspace(workspaceAfterOrder)
            val observedTotal = workspaceAfterOrder.facets.orderSummary?.total
                ?: summaryTotal
                ?: (selected.price + REFERENCE_DELIVERY_FEE)

            _orderSummaryTotal.value = observedTotal

            val checkout = api.postCheckout(
                CheckoutRequest(
                    paymentReference = BffClient.SESSION_PAYMENT_REFERENCE,
                    observedTotal = observedTotal
                )
            )

            val orderId = checkout.orderId
                ?: orderAccepted.orderId
                ?: "pending"
            val status = when {
                checkout.confirmed == true -> "CONFIRMED"
                checkout.declineCode != null -> "DECLINED"
                checkout.accepted -> "SUBMITTED"
                else -> checkout.status?.uppercase() ?: "SUBMITTED"
            }
            _sharedUnderstanding.value = _sharedUnderstanding.value.copy(cardMessage = cardMessage)
            _orderResult.value = OrderResult(
                orderId = orderId,
                status = status,
                estimatedDelivery = "Today ($today afternoon window)",
                totalAmount = observedTotal,
                declineCode = checkout.declineCode
            )
            _currentStage.value = JourneyStage.TRACKING
        }
    }

    /**
     * Reset journey UI and mint a **new** BFF session (#366).
     * Clears BffClient cookie jar + CSRF before createSession (BFF reuses cookies
     * on POST /session), then refreshes shared-understanding so contextVersion
     * matches the server before the next Need message.
     */
    suspend fun startOver() {
        _currentStage.value = JourneyStage.NEED
        _selectedArrangement.value = null
        _orderResult.value = null
        _orderSummaryTotal.value = null
        _errorMessage.value = null
        _sharedUnderstanding.value = SharedUnderstanding()
        _messages.value = listOf(
            ChatMessage(
                id = "welcome",
                sender = "florist",
                text = "Welcome to Lily's Florist. Who are we celebrating today, and when do you need the delivery?"
            )
        )
        _arrangements.value = localFallbackCatalog
        usingLocalCatalogFallback = true
        contextVersion = 0
        _sessionReady.value = false
        runGuarded {
            // Clear cookie jar before createSession so BFF mints a new session
            // instead of reusing __Host-aea_session / __Host-aea_recall (#366).
            api.clearSessionState()
            api.createSession()
            _sessionReady.value = true
            // Adopt authoritative context_version (usually 0) before the user types.
            refreshSharedUnderstanding()
            refreshCatalogFromWorkspace()
        }
    }

    fun isUsingLocalCatalogFallback(): Boolean = usingLocalCatalogFallback

    private suspend fun ensureSessionInternal() {
        if (!_sessionReady.value) {
            api.createSession()
            _sessionReady.value = true
        }
    }

    private suspend fun refreshSharedUnderstanding() {
        val remote: SharedUnderstandingResponse = api.getSharedUnderstanding()
        if (remote.contextVersion > 0) {
            contextVersion = remote.contextVersion
        }
        val intent = remote.structuredIntent
        val previous = _sharedUnderstanding.value
        _sharedUnderstanding.value = previous.copy(
            occasion = intent.occasion,
            recipient = intent.recipient,
            budget = intent.budget,
            style = intent.style,
            flowerPreference = intent.flowerPreference,
            timing = intent.timing,
            deliveryDate = intent.timing,
            contextVersion = remote.contextVersion,
            disclosure = remote.disclosure,
            suggestions = remote.suggestions
        )
        // Surface disclosure once as a florist bubble when present and new.
        val disclosure = remote.disclosure?.trim().orEmpty()
        if (disclosure.isNotEmpty() && _messages.value.none { it.sender == "florist" && it.text == disclosure }) {
            _messages.value = _messages.value + ChatMessage(
                id = "disclosure-${remote.contextVersion}",
                sender = "florist",
                text = disclosure
            )
        }
    }

    private suspend fun refreshConversation() {
        val remote = api.getConversation()
        if (remote.contextVersion > 0) {
            contextVersion = maxOf(contextVersion, remote.contextVersion)
        }
        if (remote.messages.isEmpty()) return
        val mapped = remote.messages.map { it.toChatMessage() }
        val welcome = _messages.value.firstOrNull { it.id == "welcome" }
        _messages.value = listOfNotNull(welcome) + mapped
    }

    private suspend fun refreshCatalogFromWorkspace() {
        try {
            val workspace = api.getWorkspace()
            if (workspace.contextVersion > 0) {
                contextVersion = maxOf(contextVersion, workspace.contextVersion)
            }
            val items = workspace.facets.recommendations?.items.orEmpty()
            if (items.isEmpty()) {
                usingLocalCatalogFallback = true
                _arrangements.value = localFallbackCatalog
                return
            }
            val productNames = mapOf(
                "pink-flower-vase" to "Pink Flower Vase",
                "lilac-bouquet" to "Lilac Bouquet",
                "classic-rose-dozen" to "Classic Rose Dozen",
                "budget-mixed-bunch" to "Budget Mixed Bunch",
                "premium-orchid" to "Premium Orchid"
            )
            _arrangements.value = items.map { item ->
                Arrangement(
                    sku = item.productId,
                    name = productNames[item.productId] ?: item.productId,
                    price = item.price,
                    description = "Live workspace recommendation (rank ${item.rank}).",
                    available = item.available && item.availabilityStatus != "sold_out",
                    tags = listOfNotNull(
                        item.availabilityStatus.takeIf { it.isNotBlank() },
                        "score ${item.score}"
                    )
                )
            }
            usingLocalCatalogFallback = false
        } catch (_: Exception) {
            usingLocalCatalogFallback = true
            _arrangements.value = localFallbackCatalog
        }
    }

    private suspend fun refreshContextFromWorkspace() {
        try {
            adoptWorkspace(api.getWorkspace())
        } catch (_: Exception) {
            // Fall back to last known contextVersion; mutations still CAS.
        }
    }

    private fun adoptWorkspace(workspace: WorkspaceResponse) {
        if (workspace.contextVersion > 0) {
            contextVersion = maxOf(contextVersion, workspace.contextVersion)
        }
        workspace.facets.orderSummary?.total?.let { total ->
            _orderSummaryTotal.value = total
        }
    }

    private fun adoptStaleContext(ex: BffException) {
        ex.contextVersion?.takeIf { it > 0 }?.let { contextVersion = maxOf(contextVersion, it) }
    }

    /**
     * One-shot retry on conversation 409 stale_context (#366), mirroring selection.
     */
    private suspend fun postConversationRetryingStale(
        messageText: String,
        observedContextVersion: Int
    ): AcceptedResponse {
        return try {
            api.postConversationMessage(messageText, observedContextVersion)
        } catch (ex: BffException) {
            if (ex.statusCode == 409 && ex.errorCode == "stale_context") {
                adoptStaleContext(ex)
                refreshContextFromWorkspace()
                api.postConversationMessage(messageText, contextVersion)
            } else {
                throw ex
            }
        }
    }

    /**
     * One-shot retry on selection 409 stale_context only.
     * product_unavailable must surface to the user (no infinite retry).
     */
    private suspend fun postSelectionRetryingStale(request: SelectionRequest): AcceptedResponse {
        return try {
            api.postSelection(request)
        } catch (ex: BffException) {
            if (ex.statusCode == 409 && ex.errorCode == "stale_context") {
                adoptStaleContext(ex)
                refreshContextFromWorkspace()
                api.postSelection(request.copy(observedContextVersion = contextVersion))
            } else {
                throw ex
            }
        }
    }

    private suspend fun postDeliveryRetryingStale(request: DeliveryRequest): AcceptedResponse {
        return try {
            api.postDelivery(request)
        } catch (ex: BffException) {
            if (ex.statusCode == 409 && ex.errorCode == "stale_context") {
                adoptStaleContext(ex)
                refreshContextFromWorkspace()
                api.postDelivery(request.copy(observedContextVersion = contextVersion))
            } else {
                throw ex
            }
        }
    }

    private suspend fun runGuarded(block: suspend () -> Unit) {
        _isLoading.value = true
        _errorMessage.value = null
        try {
            block()
        } catch (ex: BffException) {
            _errorMessage.value = ex.userMessage
        } catch (ex: Exception) {
            _errorMessage.value = ex.message?.takeIf { it.isNotBlank() }
                ?: "Unexpected companion error"
        } finally {
            _isLoading.value = false
        }
    }

    private fun ConversationMessageDto.toChatMessage(): ChatMessage {
        val sender = when (role.lowercase()) {
            "customer", "user" -> "user"
            else -> "florist"
        }
        return ChatMessage(
            id = messageId.ifBlank { UUID.randomUUID().toString() },
            sender = sender,
            text = text
        )
    }

    companion object {
        /** Matches platform aea_platform.pricing.REFERENCE_DELIVERY_FEE. */
        const val REFERENCE_DELIVERY_FEE = 12.0
    }
}
