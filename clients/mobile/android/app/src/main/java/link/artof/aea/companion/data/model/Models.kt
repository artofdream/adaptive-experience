package link.artof.aea.companion.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/** POST /api/v1/session → 201 body. Cookies arrive via Set-Cookie. */
@Serializable
data class SessionCreateResponse(
    @SerialName("csrf_token") val csrfToken: String
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

/**
 * UI-facing shared understanding. Populated from BFF
 * GET /api/v1/shared-understanding (`structured_intent` + context_version).
 * Occasion unlock (#357) comes from live `structured_intent.occasion`, not keywords.
 */
@Serializable
data class SharedUnderstanding(
    val occasion: String? = null,
    val recipient: String? = null,
    val budget: String? = null,
    val style: String? = null,
    @SerialName("flower_preference") val flowerPreference: String? = null,
    val timing: String? = null,
    @SerialName("delivery_date") val deliveryDate: String? = null,
    @SerialName("card_message") val cardMessage: String? = null,
    @SerialName("selected_sku") val selectedSku: String? = null,
    @SerialName("context_version") val contextVersion: Int = 0,
    val disclosure: String? = null,
    val suggestions: List<String> = emptyList(),
    val stage: String = "need"
)

@Serializable
data class StructuredIntent(
    val occasion: String? = null,
    val budget: String? = null,
    val recipient: String? = null,
    val style: String? = null,
    @SerialName("flower_preference") val flowerPreference: String? = null,
    val timing: String? = null
)

@Serializable
data class SharedUnderstandingResponse(
    @SerialName("context_version") val contextVersion: Int = 0,
    @SerialName("structured_intent") val structuredIntent: StructuredIntent = StructuredIntent(),
    val suggestions: List<String> = emptyList(),
    @SerialName("ai_generated") val aiGenerated: Boolean = false,
    @SerialName("assistant_mode") val assistantMode: String? = null,
    val disclosure: String? = null
)

@Serializable
data class ConversationMessageDto(
    @SerialName("message_id") val messageId: String = "",
    val role: String = "",
    val text: String = "",
    val status: String = "",
    @SerialName("submitted_at") val submittedAt: String = ""
)

@Serializable
data class ConversationResponse(
    @SerialName("context_version") val contextVersion: Int = 0,
    val messages: List<ConversationMessageDto> = emptyList()
)

/** Exact body for POST /api/v1/conversation/messages (not `content`). */
@Serializable
data class ConversationMessageRequest(
    @SerialName("message_text") val messageText: String,
    @SerialName("observed_context_version") val observedContextVersion: Int
)

@Serializable
data class AcceptedResponse(
    val accepted: Boolean = false,
    val code: String = "",
    @SerialName("message_id") val messageId: String? = null,
    @SerialName("correlation_id") val correlationId: String? = null,
    @SerialName("context_version") val contextVersion: Int = 0,
    @SerialName("ai_generated") val aiGenerated: Boolean = false,
    @SerialName("assistant_mode") val assistantMode: String? = null,
    val disclosure: String? = null,
    @SerialName("order_id") val orderId: String? = null,
    val status: String? = null,
    val pending: Boolean? = null,
    val confirmed: Boolean? = null,
    @SerialName("decline_code") val declineCode: String? = null
)

@Serializable
data class SelectionRequest(
    @SerialName("product_id") val productId: String,
    val items: List<SelectionItem>? = null,
    val options: Map<String, String> = emptyMap(),
    @SerialName("observed_context_version") val observedContextVersion: Int
)

@Serializable
data class SelectionItem(
    @SerialName("product_id") val productId: String,
    val quantity: Int = 1
)

@Serializable
data class DeliveryTiming(
    val date: String,
    val window: String
)

@Serializable
data class DeliveryDetails(
    val timing: DeliveryTiming,
    @SerialName("destination_reference") val destinationReference: String
)

@Serializable
data class DeliveryRequest(
    val delivery: DeliveryDetails,
    @SerialName("observed_context_version") val observedContextVersion: Int
)

/** Checkout body: ONLY payment_reference + observed_total (no raw card fields). */
@Serializable
data class CheckoutRequest(
    @SerialName("payment_reference") val paymentReference: String,
    @SerialName("observed_total") val observedTotal: Double
)

@Serializable
data class RecommendationItem(
    @SerialName("product_id") val productId: String,
    val price: Double = 0.0,
    val score: Double = 0.0,
    val rank: Int = 0,
    val available: Boolean = true,
    @SerialName("availability_status") val availabilityStatus: String = ""
)

@Serializable
data class RecommendationsFacet(
    val items: List<RecommendationItem> = emptyList()
)

@Serializable
data class WorkspaceFacets(
    val recommendations: RecommendationsFacet? = null,
    @SerialName("order_summary") val orderSummary: OrderSummaryFacet? = null,
    val order: OrderFacet? = null
)

@Serializable
data class OrderSummaryFacet(
    val total: Double? = null,
    val currency: String? = null
)

@Serializable
data class OrderFacet(
    @SerialName("order_id") val orderId: String? = null,
    val status: String? = null,
    @SerialName("authoritative_status") val authoritativeStatus: String? = null
)

@Serializable
data class WorkspaceResponse(
    @SerialName("context_version") val contextVersion: Int = 0,
    val facets: WorkspaceFacets = WorkspaceFacets(),
    val disclosure: String? = null
)

@Serializable
data class OrderResult(
    @SerialName("order_id") val orderId: String,
    val status: String,
    @SerialName("estimated_delivery") val estimatedDelivery: String = "",
    @SerialName("total_amount") val totalAmount: Double = 0.0,
    @SerialName("decline_code") val declineCode: String? = null
)

/** Mapped BFF HTTP failure for clear companion UI (401/403/503). */
class BffException(
    val statusCode: Int,
    val errorCode: String,
    override val message: String
) : Exception(message) {
    val userMessage: String
        get() = when (statusCode) {
            401 -> "Session expired or authentication required. Restart the companion to continue."
            403 -> "Request blocked (CSRF or origin). Restart the session, then try again."
            503 -> "AEA service temporarily unavailable. Try again shortly."
            429 -> "Too many requests. Wait a moment, then try again."
            409 -> "Workspace changed while editing. Refresh and retry."
            else -> message.ifBlank { "Request failed ($statusCode $errorCode)" }
        }
}
