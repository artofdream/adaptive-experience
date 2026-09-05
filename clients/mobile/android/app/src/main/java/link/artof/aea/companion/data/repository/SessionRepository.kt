package link.artof.aea.companion.data.repository

import link.artof.aea.companion.data.api.BffClient
import link.artof.aea.companion.data.model.AcceptedResponse
import link.artof.aea.companion.data.model.Arrangement
import link.artof.aea.companion.data.model.CatalogArt
import link.artof.aea.companion.data.model.BffException
import link.artof.aea.companion.data.model.ChatMessage
import link.artof.aea.companion.data.model.CheckoutRequest
import link.artof.aea.companion.data.model.CorrectionRequest
import link.artof.aea.companion.data.model.ConversationMessageDto
import link.artof.aea.companion.data.model.DeliveryDetails
import link.artof.aea.companion.data.model.DeliveryRequest
import link.artof.aea.companion.data.model.DeliveryTiming
import link.artof.aea.companion.data.model.OrderResult
import link.artof.aea.companion.data.model.SelectionRequest
import link.artof.aea.companion.data.model.SharedUnderstanding
import link.artof.aea.companion.data.model.SharedUnderstandingResponse
import link.artof.aea.companion.data.model.WorkspaceResponse
import link.artof.aea.companion.data.wallet.EdgeWallet
import link.artof.aea.companion.data.wallet.InMemoryWalletStore
import link.artof.aea.companion.data.wallet.ReorderReference
import link.artof.aea.companion.data.wallet.WalletReceipt
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.serialization.json.JsonPrimitive
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
 * Budget ask on Need (#359): chips/skip → PATCH shared-understanding + local catalog filter.
 */
class SessionRepository(
    private val api: BffClient = BffClient(),
    /**
     * ADR-020 Layer 2 device-owned Edge Wallet. Defaults to an in-memory store
     * so tests and non-Android construction stay dependency-free; the app
     * injects an EncryptedPrefsWalletStore-backed wallet (Android Keystore).
     */
    private val wallet: EdgeWallet = EdgeWallet(InMemoryWalletStore())
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
                    imageUrl = CatalogArt.imageUrlFor("classic-rose-dozen"),
            name = "Classic Rose Dozen",
            price = 70.00,
            description = "Reference catalog roses (local fallback when workspace catalog unavailable).",
            available = true,
            tags = listOf("Same-Day", "Best Seller")
        ),
        Arrangement(
            sku = "budget-mixed-bunch",
                    imageUrl = CatalogArt.imageUrlFor("budget-mixed-bunch"),
            name = "Budget Mixed Bunch",
            price = 35.00,
            description = "Value mixed bunch from reference catalog.",
            available = true,
            tags = listOf("Budget")
        ),
        Arrangement(
            sku = "lilac-bouquet",
                    imageUrl = CatalogArt.imageUrlFor("lilac-bouquet"),
            name = "Lilac Bouquet",
            price = 95.00,
            description = "Seasonal lilac bouquet.",
            available = true,
            tags = listOf("Premium")
        ),
        Arrangement(
            sku = "peony-sold-out-local",
                    imageUrl = CatalogArt.imageUrlFor("peony-sold-out-local"),
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

    /** T-04 / FR-003 quantity (web `#quantity` min 1 max 10). Default 1. */
    private val _quantity = MutableStateFlow(QUANTITY_MIN)
    val quantity: StateFlow<Int> = _quantity.asStateFlow()

    private val _sharedUnderstanding = MutableStateFlow(SharedUnderstanding())
    val sharedUnderstanding: StateFlow<SharedUnderstanding> = _sharedUnderstanding.asStateFlow()

    /**
     * True after explicit Skip or a budget chip/correction (#359).
     * Also true when live structured_intent already carries budget (e.g. Anniversary $80 chip).
     */
    private val _budgetPromptResolved = MutableStateFlow(false)
    val budgetPromptResolved: StateFlow<Boolean> = _budgetPromptResolved.asStateFlow()

    /** Local band for catalog filter (#387). Null floor/ceiling = open side; both null = no filter. */
    private var budgetFloor: Double? = null
    private var budgetCeiling: Double? = null
    /** Shopper-facing chip/band label (#388); survives BFF numeric budget coercion. */
    private var budgetChipLabel: String? = null
    /** Unfiltered workspace/fallback catalog; [_arrangements] may be budget-filtered (#359). */
    private var fullCatalog: List<Arrangement> = localFallbackCatalog

    private val _orderResult = MutableStateFlow<OrderResult?>(null)
    val orderResult: StateFlow<OrderResult?> = _orderResult.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    /** ADR-020 Layer 2: reactive device-held latest wallet receipt for returning-customer affordance. */
    private val _latestWalletReceipt = MutableStateFlow<WalletReceipt?>(wallet.latestReceipt())
    val latestWalletReceipt: StateFlow<WalletReceipt?> = _latestWalletReceipt.asStateFlow()

    private val _sessionReady = MutableStateFlow(false)
    val sessionReady: StateFlow<Boolean> = _sessionReady.asStateFlow()

    /** Authoritative checkout total from workspace order_summary (product + delivery). */
    private val _orderSummaryTotal = MutableStateFlow<Double?>(null)
    val orderSummaryTotal: StateFlow<Double?> = _orderSummaryTotal.asStateFlow()

    /** T-05: shopper-chosen FR-014 window (not hardcoded afternoon) (#381). */
    private val _deliveryWindow = MutableStateFlow("afternoon")
    val deliveryWindow: StateFlow<String> = _deliveryWindow.asStateFlow()

    /** T-05: opaque destination ref (not hardcoded home-only) (#381). */
    private val _destinationReference = MutableStateFlow(BffClient.SESSION_DESTINATION_REFERENCE)
    val destinationReference: StateFlow<String> = _destinationReference.asStateFlow()

    /** T-05: ISO date; default today. Tomorrow is the other allowlisted chip. */
    private val _deliveryDate = MutableStateFlow(LocalDate.now().toString())
    val deliveryDate: StateFlow<String> = _deliveryDate.asStateFlow()

    private val _escalationAck = MutableStateFlow<String?>(null)
    val escalationAck: StateFlow<String?> = _escalationAck.asStateFlow()

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
     * Need Continue gate (#400). Web Path B:
     * - Need steps 1–2 always open (`unlockedThrough` starts at 2)
     * - Pick (step 3) unlocks on any non-empty `structured_intent` facet
     *   (`intentKeys` in app.js), not occasion alone.
     * Companion previously required `structured_intent.occasion`, so free-text
     * that missed ReferenceIntentInterpreter.OCCASIONS stayed stuck.
     *
     * Unlock: any usable intent facet, or persisted/draft Need text (conversation
     * is first-class; parse-miss still proceeds). Budget (#359) still required
     * when occasion *is* known.
     */
    fun canContinueFromNeed(
        occasion: String? = _sharedUnderstanding.value.occasion,
        budgetPromptResolved: Boolean = _budgetPromptResolved.value,
        hasPersistedNeedText: Boolean = _messages.value.any { it.sender == "user" },
        draftNeedText: String = "",
        hasUsableIntentFacet: Boolean = hasUsableIntentFacet(_sharedUnderstanding.value),
    ): Boolean = Companion.canContinueFromNeed(
        occasion = occasion,
        budgetPromptResolved = budgetPromptResolved,
        hasPersistedNeedText = hasPersistedNeedText,
        draftNeedText = draftNeedText,
        hasUsableIntentFacet = hasUsableIntentFacet,
    )

    /**
     * Persist any unsent Need draft (web conversation POST), then enter Pick.
     * Stays on Need if the draft post fails so intent is not dropped.
     */
    suspend fun continueToPick(draftText: String = "") {
        val trimmed = draftText.trim()
        if (trimmed.isNotEmpty()) {
            postUserMessage(trimmed)
            if (_errorMessage.value != null) return
        }
        moveToPickStage()
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
        applyBudgetFilterToArrangements()
    }

    /**
     * Budget chip on Need (#359). Persists via PATCH shared-understanding (web Path B
     * correction path). Local ceiling filters catalog by arrangement.price when set.
     */
    suspend fun setBudgetChoice(label: String, ceiling: Double?) {
        runGuarded {
            ensureSessionInternal()
            val unlimited = isUnlimitedBudgetLabel(label)
            val band = if (unlimited) {
                BudgetBand(NO_LIMIT_LABEL, floor = null, ceiling = null)
            } else {
                parseBudgetBand(label) ?: BudgetBand(label, floor = null, ceiling = ceiling)
            }
            // Prefer explicit chip ceiling arg when band had no ceiling ($100+ uses floor only).
            // No limit: no local filter; PATCH schema-max 10000 (platform [1, 10000]).
            budgetFloor = band.floor
            budgetCeiling = if (unlimited) null else (band.ceiling ?: ceiling)
            val displayLabel = if (unlimited) NO_LIMIT_LABEL else label
            budgetChipLabel = displayLabel
            _budgetPromptResolved.value = true
            _sharedUnderstanding.value = _sharedUnderstanding.value.copy(budget = displayLabel)
            _messages.value = _messages.value + ChatMessage(
                id = UUID.randomUUID().toString(),
                sender = "user",
                text = "Budget: $displayLabel"
            )
            val correctionValue = when {
                unlimited -> UNLIMITED_BUDGET_SENTINEL
                budgetCeiling != null -> budgetCeiling!!
                budgetFloor != null -> budgetFloor!!
                else -> 250.0
            }
            val corrections = mapOf("budget" to JsonPrimitive(correctionValue))
            val accepted = patchCorrectionRetryingStale(corrections)
            if (accepted.contextVersion > 0) {
                contextVersion = accepted.contextVersion
            }
            refreshSharedUnderstanding()
            // Keep chip band + label (refresh may coerce numeric budget from BFF) (#388).
            budgetFloor = band.floor
            budgetCeiling = if (unlimited) null else (band.ceiling ?: ceiling)
            budgetChipLabel = displayLabel
            _sharedUnderstanding.value = _sharedUnderstanding.value.copy(budget = displayLabel)
            refreshCatalogFromWorkspace()
            applyBudgetFilterToArrangements()
        }
    }

    /**
     * Occasion correction when free-text misses OCCASIONS keywords (#400).
     * Same PATCH shared-understanding path as budget chips / web T-02.
     */
    suspend fun setOccasionChoice(label: String) {
        val token = normalizeOccasionToken(label) ?: return
        runGuarded {
            ensureSessionInternal()
            _sharedUnderstanding.value = _sharedUnderstanding.value.copy(occasion = token)
            _messages.value = _messages.value + ChatMessage(
                id = UUID.randomUUID().toString(),
                sender = "user",
                text = "Occasion: $token"
            )
            val accepted = patchCorrectionRetryingStale(
                mapOf("occasion" to JsonPrimitive(token))
            )
            if (accepted.contextVersion > 0) {
                contextVersion = accepted.contextVersion
            }
            refreshSharedUnderstanding()
            _sharedUnderstanding.value = _sharedUnderstanding.value.copy(occasion = token)
        }
    }

    /** Explicit Skip — honesty that budget was deferred (#359). Not the No limit chip (#402). */
    fun skipBudget() {
        _budgetPromptResolved.value = true
        budgetFloor = null
        budgetCeiling = null
        budgetChipLabel = SKIPPED_BUDGET_LABEL
        if (_sharedUnderstanding.value.budget.isNullOrBlank()) {
            _sharedUnderstanding.value = _sharedUnderstanding.value.copy(budget = "skipped")
        }
        _messages.value = _messages.value + ChatMessage(
            id = UUID.randomUUID().toString(),
            sender = "user",
            text = "Skip budget for now"
        )
    }

    private fun publishCatalog(catalog: List<Arrangement>) {
        fullCatalog = catalog
        applyBudgetFilterToArrangements()
    }

    private fun applyBudgetFilterToArrangements() {
        val catalog = fullCatalog.ifEmpty { localFallbackCatalog }
        val floor = budgetFloor
        val ceiling = budgetCeiling
        if (floor == null && ceiling == null) {
            _arrangements.value = catalog
            return
        }
        val filtered = catalog.filter { arrangement ->
            val price = arrangement.price
            (floor == null || price >= floor) && (ceiling == null || price <= ceiling)
        }
        // If every SKU is outside the band, keep full catalog so Pick is not empty; honesty UI still shows band.
        _arrangements.value = filtered.ifEmpty { catalog }
    }

    private suspend fun patchCorrectionRetryingStale(
        corrections: Map<String, kotlinx.serialization.json.JsonElement>
    ): AcceptedResponse {
        val request = CorrectionRequest(
            corrections = corrections,
            observedContextVersion = contextVersion
        )
        return try {
            api.patchSharedUnderstanding(request)
        } catch (ex: BffException) {
            if (ex.statusCode == 409 && ex.errorCode == "stale_context") {
                adoptStaleContext(ex)
                refreshContextFromWorkspace()
                api.patchSharedUnderstanding(
                    CorrectionRequest(corrections, observedContextVersion = contextVersion)
                )
            } else {
                throw ex
            }
        }
    }

    /**
     * Fail-closed locally if unavailable; otherwise POST /api/v1/selection to live BFF.
     */
    suspend fun selectArrangement(arrangement: Arrangement) {
        if (!arrangement.available) return // NFR-009 fail-closed
        runGuarded {
            ensureSessionInternal()
            val accepted = api.postSelection(
                selectionWithQuantity(
                    productId = arrangement.sku,
                    quantity = _quantity.value,
                    observedContextVersion = contextVersion,
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

    /** Local clamp only (web `#quantity` 1–10). Does not POST until select / update. */
    fun setQuantity(quantity: Int) {
        _quantity.value = clampQuantity(quantity)
    }

    /**
     * Shopper changed quantity on Pick/Pay (#399). Re-POSTs selection when a
     * SKU is already chosen so workspace order_summary tracks web T-04.
     */
    suspend fun updateQuantity(quantity: Int) {
        setQuantity(quantity)
        val selected = _selectedArrangement.value ?: return
        selectArrangement(selected)
    }

    fun moveToPayStage() {
        _currentStage.value = JourneyStage.PAY
    }

    /** T-05: shopper confirms an allowlisted window (#381). */
    fun setDeliveryWindow(window: String) {
        if (window in BffClient.ALLOWED_WINDOWS) {
            _deliveryWindow.value = window
        }
    }

    /** T-05: shopper confirms an opaque destination ref — never a street (#381). */
    fun setDestinationReference(reference: String) {
        if (reference in BffClient.ALLOWED_DESTINATION_REFS) {
            _destinationReference.value = reference
        }
    }

    /** T-05: today (offset 0) or tomorrow (offset 1). Past dates rejected. */
    fun setDeliveryDateOffset(daysFromToday: Int) {
        if (daysFromToday !in 0..1) return
        _deliveryDate.value = LocalDate.now().plusDays(daysFromToday.toLong()).toString()
    }

    /**
     * T-09 Contact Florist — POST /api/v1/support/escalation with allowlisted reason.
     * App shoppers then appear on /florist inbox.
     */
    suspend fun requestEscalation(reason: String) {
        val trimmed = reason.trim()
        if (trimmed !in BffClient.ALLOWED_ESCALATION_REASONS) {
            _errorMessage.value = "Choose why you need a florist (unresolved request, order, delivery, or product)."
            return
        }
        runGuarded {
            ensureSessionInternal()
            val result = api.postEscalation(trimmed)
            _escalationAck.value = result.acknowledgement
                ?: "A florist will follow up on this session."
        }
    }

    /** Pick → Need: clear local selection so Pick does not keep a stale card (#365). */
    fun backToNeed() {
        _selectedArrangement.value = null
        _sharedUnderstanding.value = _sharedUnderstanding.value.copy(selectedSku = null)
        _orderSummaryTotal.value = null
        _quantity.value = QUANTITY_MIN
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
        return product * _quantity.value + REFERENCE_DELIVERY_FEE
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

            val extraOptions = if (cardMessage.isNotBlank()) {
                mapOf("card_message" to cardMessage.take(280))
            } else {
                emptyMap()
            }
            val selectAccepted = postSelectionRetryingStale(
                selectionWithQuantity(
                    productId = selected.sku,
                    quantity = _quantity.value,
                    observedContextVersion = contextVersion,
                    extraOptions = extraOptions,
                )
            )
            if (selectAccepted.contextVersion > 0) {
                contextVersion = selectAccepted.contextVersion
            }

            val chosenDate = _deliveryDate.value
            val chosenWindow = _deliveryWindow.value
            val chosenDest = _destinationReference.value
            val deliveryAccepted = postDeliveryRetryingStale(
                DeliveryRequest(
                    delivery = DeliveryDetails(
                        timing = DeliveryTiming(date = chosenDate, window = chosenWindow),
                        destinationReference = chosenDest
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
                estimatedDelivery = "$chosenDate $chosenWindow → $chosenDest",
                totalAmount = observedTotal,
                declineCode = checkout.declineCode
            )

            // ADR-020 Layer 2: record the order in the device-owned Edge Wallet so
            // a later FR-008 reorder can present the opaque reference without the
            // platform holding any PII. Recipient label and card message are
            // DEVICE-ONLY convenience fields; only the opaque product/order ids are
            // ever surfaced back to the platform (see EdgeWallet.reorderReference).
            if (status != "DECLINED" && orderId.isNotBlank() && orderId != "pending") {
                val intent = _sharedUnderstanding.value
                val receipt = wallet.saveReceipt(
                    orderReference = orderId,
                    productId = selected.sku,
                    recipientLabel = intent.recipient,
                    cardMessageDraft = cardMessage,
                    occasionType = intent.occasion,
                )
                _latestWalletReceipt.value = receipt
            }

            _currentStage.value = JourneyStage.TRACKING
        }
    }

    /**
     * ADR-020 Layer 2: opaque-only reorder reference held on-device, or null when
     * the wallet has no prior order. Surfaces a returning-customer one-tap path
     * (FR-008) without a server-side CRM. Carries no recipient/card/PII.
     */
    fun walletReorderReference(): ReorderReference? = wallet.reorderReference()

    /** Device-held order count for a returning-customer affordance (no PII). */
    fun walletReceiptCount(): Int = wallet.receipts().size

    /** ADR-020 Layer 2: device-held latest wallet receipt (contains device-only recipient label / occasion). */
    fun latestWalletReceipt(): WalletReceipt? = wallet.latestReceipt()

    /** Clear device-held wallet history (Right-to-be-forgotten / customer sign-out). */
    fun clearWallet() {
        wallet.clear()
        _latestWalletReceipt.value = null
    }

    /**
     * FR-008 one-tap reorder from the Edge Wallet: mint/ensure a session and
     * re-select the device-held opaque product reference. Inventory is
     * authoritatively revalidated at selection (NFR-009 fail-closed), so a
     * no-longer-available product surfaces as an error rather than reordering.
     * Returns false when the wallet is empty.
     */
    suspend fun reorderFromWallet(): Boolean {
        val reference = wallet.reorderReference() ?: return false
        runGuarded {
            _currentStage.value = JourneyStage.PICK
            ensureSessionInternal()
            refreshContextFromWorkspace()
            val accepted = postSelectionRetryingStale(
                selectionWithQuantity(
                    productId = reference.productId,
                    quantity = _quantity.value,
                    observedContextVersion = contextVersion,
                )
            )
            if (accepted.contextVersion > 0) {
                contextVersion = accepted.contextVersion
            }
            _sharedUnderstanding.value =
                _sharedUnderstanding.value.copy(selectedSku = reference.productId)
            refreshCatalogFromWorkspace()
            _selectedArrangement.value =
                _arrangements.value.firstOrNull { it.sku == reference.productId }
            refreshSharedUnderstanding()
        }
        return true
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
        _quantity.value = QUANTITY_MIN
        _errorMessage.value = null
        _deliveryWindow.value = "afternoon"
        _destinationReference.value = BffClient.SESSION_DESTINATION_REFERENCE
        _deliveryDate.value = LocalDate.now().toString()
        _escalationAck.value = null
        _sharedUnderstanding.value = SharedUnderstanding()
        _budgetPromptResolved.value = false
        budgetFloor = null
        budgetCeiling = null
        budgetChipLabel = null
        _latestWalletReceipt.value = wallet.latestReceipt()
        _messages.value = listOf(
            ChatMessage(
                id = "welcome",
                sender = "florist",
                text = "Welcome to Lily's Florist. Who are we celebrating today, and when do you need the delivery?"
            )
        )
        publishCatalog(localFallbackCatalog)
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
        val displayBudget = when {
            !budgetChipLabel.isNullOrBlank() -> displayBudgetLabel(budgetChipLabel)
            !intent.budget.isNullOrBlank() -> displayBudgetLabel(intent.budget)
            else -> displayBudgetLabel(previous.budget)
        }
        _sharedUnderstanding.value = previous.copy(
            occasion = intent.occasion,
            recipient = intent.recipient,
            budget = displayBudget,
            style = intent.style,
            flowerPreference = intent.flowerPreference,
            timing = intent.timing,
            deliveryDate = intent.timing,
            contextVersion = remote.contextVersion,
            disclosure = remote.disclosure,
            suggestions = remote.suggestions
        )
        if (!intent.budget.isNullOrBlank()) {
            _budgetPromptResolved.value = true
            // Apply soft ceiling from live numeric intent only when no chip band is active.
            // Schema-max 10000 is the No limit sentinel — do not treat it as a ceiling.
            if (budgetFloor == null && budgetCeiling == null && !isUnlimitedBudgetLabel(intent.budget)) {
                val band = parseBudgetBand(intent.budget)
                if (band != null) {
                    budgetFloor = band.floor
                    budgetCeiling = band.ceiling
                } else {
                    parseBudgetCeiling(intent.budget)?.let { budgetCeiling = it }
                }
            }
        }
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
                publishCatalog(localFallbackCatalog)
                return
            }
            val productNames = mapOf(
                "pink-flower-vase" to "Pink Flower Vase",
                "lilac-bouquet" to "Lilac Bouquet",
                "classic-rose-dozen" to "Classic Rose Dozen",
                "budget-mixed-bunch" to "Budget Mixed Bunch",
                "premium-orchid" to "Premium Orchid"
            )
            publishCatalog(items.map { item ->
                Arrangement(
                    sku = item.productId,
                    name = productNames[item.productId] ?: item.productId,
                    price = item.price,
                    description = "Live workspace recommendation (rank ${item.rank}).",
                    imageUrl = CatalogArt.imageUrlFor(item.productId),
                    available = item.available && item.availabilityStatus != "sold_out",
                    tags = listOfNotNull(
                        item.availabilityStatus.takeIf { it.isNotBlank() },
                        "score ${item.score}"
                    )
                )
            })
            usingLocalCatalogFallback = false
        } catch (_: Exception) {
            usingLocalCatalogFallback = true
            publishCatalog(localFallbackCatalog)
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

        /** Need chip label for an explicit no-budget-constraint (#402). */
        const val NO_LIMIT_LABEL = "No limit"

        /** Need chip / local fact when the customer deferred budget (#359). */
        const val SKIPPED_BUDGET_LABEL = "skipped"

        /**
         * Platform `_facets` budget max (1..10000). Companion No limit PATCHes this
         * number so florist/operator get a real fact without a new facet.
         */
        const val UNLIMITED_BUDGET_SENTINEL = 10000.0

        /** Matches platform aea_platform.selection QUANTITY_MIN / QUANTITY_MAX and web `#quantity`. */
        const val QUANTITY_MIN = 1
        const val QUANTITY_MAX = 10

        fun clampQuantity(value: Int): Int = value.coerceIn(QUANTITY_MIN, QUANTITY_MAX)

        /**
         * Web T-04 customize body (#399): `product_id` + `options.quantity`.
         * BFF accepts int or string; companion sends string because
         * [SelectionRequest.options] is Map<String, String>. Multi-SKU
         * `items[]` is deferred (web cart increment path only).
         */
        fun selectionWithQuantity(
            productId: String,
            quantity: Int,
            observedContextVersion: Int,
            extraOptions: Map<String, String> = emptyMap(),
        ): SelectionRequest {
            val qty = clampQuantity(quantity)
            return SelectionRequest(
                productId = productId,
                options = extraOptions + ("quantity" to qty.toString()),
                observedContextVersion = observedContextVersion,
            )
        }

        data class BudgetBand(val label: String, val floor: Double?, val ceiling: Double?)

        /**
         * Parse Need chip / BFF budget into an inclusive local catalog band (#387).
         * Under $50 → [null, 50]; $50–100 → [50, 100]; $100+ → [100, null];
         * skipped / No limit / blank → null band (no filter); bare number → [null, n] soft ceiling.
         */
        fun parseBudgetBand(labelOrText: String?): BudgetBand? {
            val raw = labelOrText?.trim().orEmpty()
            if (raw.isEmpty()) return null
            val normalized = raw
                .replace('–', '-')
                .replace('—', '-')
                .lowercase()
            when {
                isSkippedBudgetLabel(raw) || isUnlimitedBudgetLabel(raw) -> return null
                "100+" in normalized -> return BudgetBand(raw, floor = 100.0, ceiling = null)
                normalized.startsWith("under") -> {
                    val ceiling = Regex("""(\d+(?:\.\d+)?)""").find(normalized)
                        ?.groupValues?.get(1)
                        ?.toDoubleOrNull()
                    return BudgetBand(raw, floor = null, ceiling = ceiling)
                }
                Regex("""\$?\s*50\s*-\s*100""").containsMatchIn(normalized) ->
                    return BudgetBand(raw, floor = 50.0, ceiling = 100.0)
            }
            val number = raw.replace("$", "").replace(",", "").trim().toDoubleOrNull()
                ?: return null
            return BudgetBand(raw, floor = null, ceiling = number)
        }

        /**
         * Parse optional local catalog budget ceiling from Need chip label or BFF budget text (#359/#387).
         * Under $50 → 50; $50–100 → 100; $100+ / skipped → null;
         * bare numeric string (e.g. "75") → that Double.
         */
        /**
         * Enclosure card default for Pay (#389). Matches occasion/recipient when known;
         * empty when unknown so staff/florist can fill. Never Birthday Mom on Anniversary.
         */
        fun defaultCardMessage(occasion: String?, recipient: String?): String {
            val occ = occasion?.trim()?.lowercase().orEmpty()
            val who = recipient?.trim().orEmpty()
            val whoPart = when {
                who.isBlank() -> ""
                else -> " $who"
            }
            return when {
                occ.contains("annivers") -> "Happy Anniversary$whoPart! With love."
                occ.contains("birthday") || occ.contains("birth day") ->
                    "Happy Birthday$whoPart! Love always."
                occ.contains("thank") -> "Thank you$whoPart!"
                occ.isNotBlank() -> "Thinking of you$whoPart."
                else -> ""
            }.replace("  ", " ").trim()
        }

        /**
         * Web `intentKeys`: any non-empty structured_intent facet unlocks Pick.
         * Occasion is sufficient but not required.
         */
        fun hasUsableIntentFacet(understanding: SharedUnderstanding): Boolean {
            return listOf(
                understanding.occasion,
                understanding.recipient,
                understanding.budget,
                understanding.style,
                understanding.flowerPreference,
                understanding.timing,
            ).any { !it.isNullOrBlank() }
        }

        /** Tokens accepted by ReferenceIntentInterpreter.OCCASIONS / BFF PATCH. */
        val OCCASION_CORRECTION_TOKENS = listOf(
            "birthday",
            "anniversary",
            "wedding",
            "sympathy",
            "thank you",
        )

        fun normalizeOccasionToken(label: String): String? {
            val raw = label.trim().lowercase()
            if (raw.isEmpty()) return null
            return OCCASION_CORRECTION_TOKENS.firstOrNull { it == raw }
        }

        /**
         * Pure Need Continue predicate (#400).
         * Unlock on any usable intent facet (web Pick) or Need text (conversation
         * first-class / parse-miss). Occasion-known path still requires budget
         * chip or skip (#359) — CTA must say so, not look like Send failed.
         */
        fun canContinueFromNeed(
            occasion: String?,
            budgetPromptResolved: Boolean,
            hasPersistedNeedText: Boolean,
            draftNeedText: String = "",
            hasUsableIntentFacet: Boolean = false,
        ): Boolean {
            val hasNeed = !occasion.isNullOrBlank() ||
                hasUsableIntentFacet ||
                hasPersistedNeedText ||
                draftNeedText.isNotBlank()
            if (!hasNeed) return false
            if (!occasion.isNullOrBlank() && !budgetPromptResolved) return false
            return true
        }

        fun isSkippedBudgetLabel(labelOrText: String?): Boolean {
            return labelOrText?.trim()?.equals(SKIPPED_BUDGET_LABEL, ignoreCase = true) == true
        }

        fun isUnlimitedBudgetLabel(labelOrText: String?): Boolean {
            val normalized = labelOrText?.trim()?.lowercase().orEmpty()
            if (normalized.isEmpty()) return false
            if (normalized == NO_LIMIT_LABEL.lowercase() || normalized == "unlimited") return true
            val number = normalized.replace("$", "").replace(",", "").toDoubleOrNull()
            return number != null && number == UNLIMITED_BUDGET_SENTINEL
        }

        /** Chip / florist-facing budget label. Maps schema-max 10000 → No limit (#402). */
        fun displayBudgetLabel(labelOrText: String?): String? {
            val raw = labelOrText?.trim().orEmpty()
            if (raw.isEmpty()) return null
            if (isSkippedBudgetLabel(raw)) return SKIPPED_BUDGET_LABEL
            if (isUnlimitedBudgetLabel(raw)) return NO_LIMIT_LABEL
            return raw
        }

        fun pickBudgetCaption(budgetLabel: String?): String? {
            val label = displayBudgetLabel(budgetLabel) ?: return null
            return when (label) {
                SKIPPED_BUDGET_LABEL -> "Budget not set (skipped on Need)."
                NO_LIMIT_LABEL -> "No budget limit — full catalog (No limit on Need)."
                else ->
                    "Filtering / ranking with budget: $label (local price filter when catalog has prices)."
            }
        }

        fun payBudgetCaption(budgetHonesty: String?, selectedPrice: Double?): String? {
            val label = displayBudgetLabel(budgetHonesty) ?: return null
            if (label == SKIPPED_BUDGET_LABEL) return "Budget: skipped on Need"
            if (label == NO_LIMIT_LABEL) return "Budget: No limit"
            val ceiling = parseBudgetCeiling(label)
            return if (ceiling != null && selectedPrice != null && selectedPrice > ceiling) {
                "Budget: $label — selected price exceeds ceiling"
            } else {
                "Budget: $label"
            }
        }

        fun parseBudgetCeiling(labelOrText: String?): Double? {
            val raw = labelOrText?.trim().orEmpty()
            if (raw.isEmpty()) return null
            val normalized = raw
                .replace('\u2013', '-') // en-dash (chip "$50–100")
                .replace('\u2014', '-') // em-dash
                .lowercase()
            when {
                isSkippedBudgetLabel(raw) || isUnlimitedBudgetLabel(raw) -> return null
                "100+" in normalized -> return null
                normalized.startsWith("under") -> {
                    return Regex("""(\d+(?:\.\d+)?)""").find(normalized)
                        ?.groupValues?.get(1)
                        ?.toDoubleOrNull()
                }
                Regex("""\$?\s*50\s*-\s*100""").containsMatchIn(normalized) -> return 100.0
            }
            // Bare number from BFF / live intent (e.g. Anniversary "80" / serializer "75").
            return raw.replace("$", "").replace(",", "").trim().toDoubleOrNull()
        }
    }
}
