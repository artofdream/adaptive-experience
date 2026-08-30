package link.artof.aea.companion.data.repository

import link.artof.aea.companion.data.api.BffClient
import link.artof.aea.companion.data.model.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.UUID

enum class JourneyStage {
    NEED,
    PICK,
    PAY,
    TRACKING
}

class SessionRepository(
    private val api: BffClient = BffClient()
) {
    private val _currentStage = MutableStateFlow(JourneyStage.NEED)
    val currentStage: StateFlow<JourneyStage> = _currentStage.asStateFlow()

    private val _messages = MutableStateFlow<List<ChatMessage>>(listOf(
        ChatMessage(
            id = "welcome",
            sender = "florist",
            text = "Welcome to Lily\'s Florist. Who are we celebrating today, and when do you need the delivery?"
        )
    ))
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()

    private val _arrangements = MutableStateFlow<List<Arrangement>>(listOf(
        Arrangement(
            sku = "ROSE-SAME-01",
            name = "Classic Red Roses (Dozen)",
            price = 68.00,
            description = "Locally cut long-stem red roses in signature craft wrap.",
            available = true,
            tags = listOf("Same-Day Delivery", "Mother\'s Birthday", "Best Seller")
        ),
        Arrangement(
            sku = "SUN-SAME-02",
            name = "Radiant Sunflowers & Delphinium",
            price = 74.50,
            description = "Vibrant seasonal blooms conditioned for 7-day vase life.",
            available = true,
            tags = listOf("Same-Day Delivery", "Birthday Cheer")
        ),
        Arrangement(
            sku = "PEONY-SPEC-03",
            name = "Blush Peonies & Eucalyptus",
            price = 85.00,
            description = "Limited season imported blush peonies.",
            available = false, // Fail-closed example
            tags = listOf("Sold Out Today", "Pre-Order Only")
        )
    ))
    val arrangements: StateFlow<List<Arrangement>> = _arrangements.asStateFlow()

    private val _selectedArrangement = MutableStateFlow<Arrangement?>(null)
    val selectedArrangement: StateFlow<Arrangement?> = _selectedArrangement.asStateFlow()

    private val _sharedUnderstanding = MutableStateFlow(SharedUnderstanding())
    val sharedUnderstanding: StateFlow<SharedUnderstanding> = _sharedUnderstanding.asStateFlow()

    private val _orderResult = MutableStateFlow<OrderResult?>(null)
    val orderResult: StateFlow<OrderResult?> = _orderResult.asStateFlow()

    private var sessionToken: String = UUID.randomUUID().toString()

    fun postUserMessage(text: String) {
        val userMsg = ChatMessage(id = UUID.randomUUID().toString(), sender = "user", text = text)
        _messages.value = _messages.value + userMsg

        // Simulate concierge assistant response for Journey 1 (Same-Day)
        if (text.contains("Mom", ignoreCase = true) || text.contains("birthday", ignoreCase = true) || text.contains("same", ignoreCase = true)) {
            _sharedUnderstanding.value = _sharedUnderstanding.value.copy(
                occasion = "Mother\'s Birthday",
                deliveryDate = "Today (Same-Day)",
                recipient = "Mom"
            )
            val assistantReply = ChatMessage(
                id = UUID.randomUUID().toString(),
                sender = "florist",
                text = "Perfect! I have found fresh morning-harvest roses available for same-day delivery today. Tap Continue to view arrangements."
            )
            _messages.value = _messages.value + assistantReply
        }
    }

    fun moveToPickStage() {
        _currentStage.value = JourneyStage.PICK
    }

    fun selectArrangement(arrangement: Arrangement) {
        if (!arrangement.available) return // Fail-closed rule (NFR-009)
        _selectedArrangement.value = arrangement
        _sharedUnderstanding.value = _sharedUnderstanding.value.copy(selectedSku = arrangement.sku)
    }

    fun moveToPayStage() {
        _currentStage.value = JourneyStage.PAY
    }

    fun completeCheckout(cardMessage: String) {
        val selected = _selectedArrangement.value ?: return
        _sharedUnderstanding.value = _sharedUnderstanding.value.copy(cardMessage = cardMessage)
        _orderResult.value = OrderResult(
            orderId = "LF-" + (1000..9999).random(),
            status = "CONFIRMED",
            estimatedDelivery = "Today before 5:00 PM",
            totalAmount = selected.price
        )
        _currentStage.value = JourneyStage.TRACKING
    }

    fun startOver() {
        _currentStage.value = JourneyStage.NEED
        _selectedArrangement.value = null
        _orderResult.value = null
    }
}
