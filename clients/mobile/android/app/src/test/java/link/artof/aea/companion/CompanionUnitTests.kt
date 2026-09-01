package link.artof.aea.companion

import link.artof.aea.companion.data.api.BffClient
import link.artof.aea.companion.data.model.AcceptedResponse
import link.artof.aea.companion.data.model.Arrangement
import link.artof.aea.companion.data.model.CheckoutRequest
import link.artof.aea.companion.data.model.ConversationMessageRequest
import link.artof.aea.companion.data.model.ConversationResponse
import link.artof.aea.companion.data.model.DeliveryRequest
import link.artof.aea.companion.data.model.SelectionRequest
import link.artof.aea.companion.data.model.SessionCreateResponse
import link.artof.aea.companion.data.model.SharedUnderstandingResponse
import link.artof.aea.companion.data.model.StructuredIntent
import link.artof.aea.companion.data.model.WorkspaceResponse
import link.artof.aea.companion.data.repository.JourneyStage
import link.artof.aea.companion.data.repository.SessionRepository
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

class CompanionUnitTests {

    private lateinit var fakeApi: FakeBffClient
    private lateinit var repository: SessionRepository
    private val json = Json { ignoreUnknownKeys = true; isLenient = true; encodeDefaults = true; explicitNulls = false }

    @Before
    fun setup() {
        fakeApi = FakeBffClient()
        repository = SessionRepository(api = fakeApi)
    }

    @Test
    fun debugApplicationIdMatchesFirebaseClient() {
        assertEquals("link.artof.aea.companion", BuildConfig.APPLICATION_ID)
    }

    @Test
    fun testInitialStageIsNeed() {
        assertEquals(JourneyStage.NEED, repository.currentStage.value)
        assertTrue(repository.messages.value.isNotEmpty())
        assertNull(repository.selectedArrangement.value)
        assertNull(repository.orderResult.value)
    }

    @Test
    fun momKeywordAloneDoesNotUnlockOccasionWithoutBffSharedUnderstanding() = runBlocking {
        // Fake BFF returns empty structured_intent — keyword path must be gone (#357).
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(
            contextVersion = 1,
            structuredIntent = StructuredIntent()
        )
        repository.postUserMessage("I need flowers for Mom's birthday, same day delivery")
        assertNull(
            "Occasion must come from shared-understanding, not Mom keyword mock",
            repository.sharedUnderstanding.value.occasion
        )
        assertTrue(fakeApi.postedMessages.isNotEmpty())
        assertEquals("message_text contract", "I need flowers for Mom's birthday, same day delivery", fakeApi.postedMessages.last().messageText)
    }

    @Test
    fun liveSharedUnderstandingUnlocksOccasion() = runBlocking {
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(
            contextVersion = 2,
            structuredIntent = StructuredIntent(occasion = "birthday", recipient = "mother"),
            disclosure = "Automated interpretation; review and correct before ordering."
        )
        repository.postUserMessage("birthday for mother")
        assertEquals("birthday", repository.sharedUnderstanding.value.occasion)
        assertEquals("mother", repository.sharedUnderstanding.value.recipient)
        assertTrue(repository.messages.value.any { it.text.contains("Automated interpretation") })
    }

    @Test
    fun testFailClosedUnavailableArrangementCannotBeSelected() = runBlocking {
        val soldOutArrangement = Arrangement(
            sku = "PEONY-SOLD-OUT",
            name = "Blush Peonies",
            price = 85.0,
            available = false
        )

        repository.selectArrangement(soldOutArrangement)
        assertNull(repository.selectedArrangement.value)
        assertNull(repository.sharedUnderstanding.value.selectedSku)
        assertTrue("Fail-closed must not hit BFF selection", fakeApi.selections.isEmpty())
    }

    @Test
    fun testAvailableArrangementSelectionPostsToBff() = runBlocking {
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(contextVersion = 3)
        val rose = Arrangement(
            sku = "classic-rose-dozen",
            name = "Classic Roses",
            price = 70.0,
            available = true
        )
        repository.moveToPickStage()
        repository.selectArrangement(rose)
        assertEquals(rose, repository.selectedArrangement.value)
        assertEquals("classic-rose-dozen", repository.sharedUnderstanding.value.selectedSku)
        assertEquals(1, fakeApi.selections.size)
        assertEquals("classic-rose-dozen", fakeApi.selections.last().productId)
    }

    @Test
    fun checkoutUsesOrderThenOpaquePaymentReference() = runBlocking {
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(contextVersion = 4)
        val rose = Arrangement(
            sku = "classic-rose-dozen",
            name = "Classic Roses",
            price = 70.0,
            available = true
        )
        repository.moveToPickStage()
        repository.selectArrangement(rose)
        repository.moveToPayStage()
        repository.completeCheckout("Happy Birthday Mom!")
        assertEquals(JourneyStage.TRACKING, repository.currentStage.value)
        assertTrue(fakeApi.orderPosted)
        assertNotNull(fakeApi.lastCheckout)
        assertEquals(BffClient.SESSION_PAYMENT_REFERENCE, fakeApi.lastCheckout!!.paymentReference)
        assertEquals(70.0, fakeApi.lastCheckout!!.observedTotal, 0.01)
        assertEquals("CONFIRMED", repository.orderResult.value?.status)
    }

    @Test
    fun bffClientPayloadShapesMatchContract() {
        val message = ConversationMessageRequest(
            messageText = "hello",
            observedContextVersion = 0
        )
        val messageJson = json.encodeToString(message)
        assertTrue(messageJson.contains("\"message_text\""))
        assertTrue(messageJson.contains("\"observed_context_version\""))
        assertFalse("Must not use content key", messageJson.contains("\"content\""))

        val selection = SelectionRequest(
            productId = "classic-rose-dozen",
            observedContextVersion = 2
        )
        val selectionJson = json.encodeToString(selection)
        assertTrue(selectionJson.contains("\"product_id\""))
        assertFalse(selectionJson.contains("\"sku\""))

        val checkout = CheckoutRequest(
            paymentReference = BffClient.SESSION_PAYMENT_REFERENCE,
            observedTotal = 70.0
        )
        val checkoutJson = json.encodeToString(checkout)
        assertTrue(checkoutJson.contains("\"payment_reference\""))
        assertTrue(checkoutJson.contains("\"observed_total\""))
        assertFalse(checkoutJson.contains("card_number"))
        assertFalse(checkoutJson.contains("session_token"))

        val session = SessionCreateResponse(csrfToken = "abc")
        assertEquals("abc", session.csrfToken)
        assertEquals("https://aea.artof.link", BffClient.DEFAULT_BASE_URL)
    }

    @Test
    fun testBffJsonSerialization() {
        val arrangement = Arrangement(
            sku = "LILY-TEST",
            name = "Stargazer Lilies",
            price = 59.99,
            available = true,
            tags = listOf("Fragrant", "Same-Day")
        )

        val serialized = json.encodeToString(arrangement)
        assertTrue(serialized.contains("LILY-TEST"))
        assertTrue(serialized.contains("59.99"))

        val deserialized = json.decodeFromString<Arrangement>(serialized)
        assertEquals("LILY-TEST", deserialized.sku)
        assertEquals(59.99, deserialized.price, 0.01)
    }
}

/** In-memory BFF stand-in for unit tests (no network). */
class FakeBffClient : BffClient() {
    var sharedUnderstanding: SharedUnderstandingResponse = SharedUnderstandingResponse()
    val postedMessages = mutableListOf<ConversationMessageRequest>()
    val selections = mutableListOf<SelectionRequest>()
    var orderPosted: Boolean = false
    var lastCheckout: CheckoutRequest? = null
    private var version: Int = 0

    override suspend fun createSession(): SessionCreateResponse {
        return SessionCreateResponse(csrfToken = "test-csrf")
    }

    override suspend fun postConversationMessage(
        messageText: String,
        observedContextVersion: Int
    ): AcceptedResponse {
        postedMessages += ConversationMessageRequest(messageText, observedContextVersion)
        version = observedContextVersion + 1
        return AcceptedResponse(accepted = true, code = "accepted", contextVersion = version)
    }

    override suspend fun getSharedUnderstanding(): SharedUnderstandingResponse {
        return sharedUnderstanding.copy(contextVersion = maxOf(sharedUnderstanding.contextVersion, version))
    }

    override suspend fun getConversation(): ConversationResponse {
        return ConversationResponse(contextVersion = version, messages = emptyList())
    }

    override suspend fun getWorkspace(): WorkspaceResponse = WorkspaceResponse(contextVersion = version)

    override suspend fun postSelection(request: SelectionRequest): AcceptedResponse {
        selections += request
        version = request.observedContextVersion + 1
        return AcceptedResponse(accepted = true, code = "accepted", contextVersion = version)
    }

    override suspend fun postDelivery(request: DeliveryRequest): AcceptedResponse {
        version = request.observedContextVersion + 1
        return AcceptedResponse(accepted = true, code = "accepted", contextVersion = version)
    }

    override suspend fun postOrder(): AcceptedResponse {
        orderPosted = true
        return AcceptedResponse(accepted = true, code = "accepted", orderId = "ord-test", status = "created")
    }

    override suspend fun postCheckout(request: CheckoutRequest): AcceptedResponse {
        lastCheckout = request
        return AcceptedResponse(
            accepted = true,
            code = "accepted",
            orderId = "ord-test",
            status = "submitted",
            confirmed = true,
            pending = true
        )
    }
}
