package link.artof.aea.companion.data.model

import kotlinx.serialization.KSerializer
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.descriptors.PrimitiveKind
import kotlinx.serialization.descriptors.PrimitiveSerialDescriptor
import kotlinx.serialization.descriptors.SerialDescriptor
import kotlinx.serialization.encoding.Decoder
import kotlinx.serialization.encoding.Encoder
import kotlinx.serialization.json.JsonDecoder
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonPrimitive

/** POST /api/v1/session → 201 body. Cookies arrive via Set-Cookie. */
@Serializable
data class SessionCreateResponse(
    @SerialName("csrf_token") val csrfToken: String
)


/**
 * BFF may return budget as a JSON number (platform float) or string.
 * Normalize to string for companion display / local ceiling parse (#359).
 */
object BudgetAsStringSerializer : KSerializer<String> {
    override val descriptor: SerialDescriptor =
        PrimitiveSerialDescriptor("BudgetAsString", PrimitiveKind.STRING)

    override fun serialize(encoder: Encoder, value: String) {
        encoder.encodeString(value)
    }

    override fun deserialize(decoder: Decoder): String {
        val input = decoder as? JsonDecoder ?: return decoder.decodeString()
        val element = input.decodeJsonElement()
        val primitive = element as? JsonPrimitive ?: return element.toString()
        return primitive.content
    }
}

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
    @Serializable(with = BudgetAsStringSerializer::class)
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
    @Serializable(with = BudgetAsStringSerializer::class)
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

/** PATCH /api/v1/shared-understanding — web Path B correction shape (#359). */
@Serializable
data class CorrectionRequest(
    val corrections: Map<String, JsonElement>,
    @SerialName("observed_context_version") val observedContextVersion: Int
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

/** POST /api/v1/support/escalation — body is reason only (#381 / T-09). */
@Serializable
data class EscalationRequest(
    val reason: String
)

@Serializable
data class EscalationResponse(
    val accepted: Boolean = false,
    val code: String = "",
    @SerialName("message_id") val messageId: String? = null,
    val acknowledgement: String? = null,
    @SerialName("escalation_reason") val escalationReason: String? = null,
    @SerialName("correlation_id") val correlationId: String? = null
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

/**
 * Mapped BFF HTTP failure for clear companion UI.
 * Prefer `errorCode` from BFF JSON (`code` or `error`) when choosing copy (#365).
 */
class BffException(
    val statusCode: Int,
    val errorCode: String,
    override val message: String,
    val contextVersion: Int? = null
) : Exception(message) {
    val userMessage: String
        get() = when {
            statusCode == 401 ->
                "Session expired or authentication required. Restart the companion to continue."
            statusCode == 403 ->
                "Request blocked (CSRF or origin). Restart the session, then try again."
            statusCode == 503 ->
                "AEA service temporarily unavailable. Try again shortly."
            statusCode == 429 ->
                "Too many requests. Wait a moment, then try again."
            errorCode == "stale_context" ->
                "Workspace changed while editing. Refresh and retry."
            errorCode == "total_mismatch" ->
                "Order total is out of date (product + delivery). Refresh the summary and retry."
            errorCode == "checkout_conflict" ->
                "Checkout conflict — this order may already be in progress. Start over or retry."
            errorCode == "product_unavailable" ->
                "That product is no longer available. Go back to Pick and choose another."
            statusCode == 409 ->
                "Workspace changed while editing. Refresh and retry."
            else -> message.ifBlank { "Request failed ($statusCode $errorCode)" }
        }
}
