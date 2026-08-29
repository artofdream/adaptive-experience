package link.artof.aea.companion.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SessionResponse(
    @SerialName("session_id") val sessionId: String,
    val environment: String = "production",
    @SerialName("created_at") val createdAt: Long = 0L,
    val stage: String = "need"
)

@Serializable
data class ChatMessage(
    val id: String = "",
    val sender: String, // "user" or "florist"
    val text: String,
    val timestamp: Long = System.currentTimeMillis()
)

@Serializable
data class Arrangement(
    val sku: String,
    val name: String,
    val price: Double,
    val description: String = "",
    @SerialName("image_url") val imageUrl: String = "",
    val available: Boolean = true,
    val tags: List<String> = emptyList(),
    @SerialName("care_level") val careLevel: String = "Medium"
)

@Serializable
data class SharedUnderstanding(
    val occasion: String? = null,
    val recipient: String? = null,
    val budget: String? = null,
    @SerialName("delivery_date") val deliveryDate: String? = null,
    @SerialName("card_message") val cardMessage: String? = null,
    @SerialName("selected_sku") val selectedSku: String? = null,
    val stage: String = "need"
)

@Serializable
data class SelectionRequest(
    val sku: String
)

@Serializable
data class DeliveryRequest(
    @SerialName("recipient_reference") val recipientReference: String,
    @SerialName("delivery_slot") val deliverySlot: String,
    @SerialName("card_message") val cardMessage: String? = null
)

@Serializable
data class CheckoutRequest(
    @SerialName("session_token") val sessionToken: String,
    @SerialName("confirmation_acknowledged") val confirmationAcknowledged: Boolean = true
)

@Serializable
data class OrderResult(
    @SerialName("order_id") val orderId: String,
    val status: String,
    @SerialName("estimated_delivery") val estimatedDelivery: String = "",
    @SerialName("total_amount") val totalAmount: Double = 0.0
)
