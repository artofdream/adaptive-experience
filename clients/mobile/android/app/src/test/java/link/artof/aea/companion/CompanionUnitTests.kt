package link.artof.aea.companion

import link.artof.aea.companion.data.api.BffClient
import link.artof.aea.companion.data.model.AcceptedResponse
import link.artof.aea.companion.data.model.WorkspaceFacets
import link.artof.aea.companion.data.model.OrderSummaryFacet
import link.artof.aea.companion.data.model.BffException
import link.artof.aea.companion.data.model.Arrangement
import link.artof.aea.companion.data.model.CheckoutRequest
import link.artof.aea.companion.data.model.CorrectionRequest
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
        // Mirror web: observed_total from order_summary (product + REFERENCE_DELIVERY_FEE).
        assertEquals(82.0, fakeApi.lastCheckout!!.observedTotal, 0.01)
        assertEquals(82.0, repository.orderResult.value?.totalAmount ?: 0.0, 0.01)
        assertEquals("CONFIRMED", repository.orderResult.value?.status)
    }

    @Test
    fun backNavClearsSelectionAndStartOverFromPay() = runBlocking {
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
        assertEquals(JourneyStage.PAY, repository.currentStage.value)

        repository.backToPick()
        assertEquals(JourneyStage.PICK, repository.currentStage.value)
        assertEquals(rose, repository.selectedArrangement.value)

        repository.backToNeed()
        assertEquals(JourneyStage.NEED, repository.currentStage.value)
        assertNull(repository.selectedArrangement.value)

        repository.moveToPickStage()
        repository.selectArrangement(rose)
        repository.moveToPayStage()
        repository.startOver()
        assertEquals(JourneyStage.NEED, repository.currentStage.value)
        assertNull(repository.selectedArrangement.value)
        assertNull(repository.orderResult.value)
        assertTrue(
            "Start Over must clear BFF cookie/CSRF state before createSession (#366)",
            fakeApi.clearSessionStateCalls >= 1
        )
        assertTrue(
            "Start Over must createSession after clear (#366)",
            fakeApi.createSessionCalls >= 1
        )
        assertTrue(
            "clearSessionState must run before createSession",
            fakeApi.lastClearBeforeCreate
        )
    }

    @Test
    fun startOverClearsSessionStateThenCreatesSessionAndRefreshesUnderstanding() = runBlocking {
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(
            contextVersion = 5,
            structuredIntent = StructuredIntent(occasion = "anniversary")
        )
        // Simulate prior live session activity so createSession was already used.
        repository.ensureSession()
        assertTrue(repository.sessionReady.value)
        assertEquals(1, fakeApi.createSessionCalls)

        // Advance fake understanding version as if journey progressed.
        fakeApi.versionForTests = 7
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(
            contextVersion = 7,
            structuredIntent = StructuredIntent(occasion = "anniversary")
        )

        fakeApi.clearSessionStateCalls = 0
        fakeApi.createSessionCalls = 0
        repository.startOver()

        assertEquals(1, fakeApi.clearSessionStateCalls)
        assertEquals(1, fakeApi.createSessionCalls)
        assertTrue(fakeApi.lastClearBeforeCreate)
        assertEquals(JourneyStage.NEED, repository.currentStage.value)
        assertTrue(repository.sessionReady.value)
        // After startOver refresh, occasion comes from new-session shared-understanding.
        assertEquals("anniversary", repository.sharedUnderstanding.value.occasion)
        assertNull(repository.selectedArrangement.value)
        assertNull(repository.errorMessage.value)
    }

    @Test
    fun staleContextOnConversationRetriesOnceThenSucceeds() = runBlocking {
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(contextVersion = 2)
        fakeApi.staleConversationOnce = true
        repository.postUserMessage("Anniversary bouquet under \$80")
        assertEquals(2, fakeApi.postedMessages.size)
        assertNull(repository.errorMessage.value)
        assertTrue(repository.messages.value.any { it.text.contains("Anniversary") })
    }

    @Test
    fun displayCheckoutTotalIncludesReferenceDeliveryFee() {
        assertEquals(82.0, repository.displayCheckoutTotal(70.0), 0.01)
        assertEquals(SessionRepository.REFERENCE_DELIVERY_FEE, 12.0, 0.01)
    }

    @Test
    fun staleContextOnSelectionRetriesOnceThenSucceeds() = runBlocking {
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(contextVersion = 4)
        val rose = Arrangement(
            sku = "classic-rose-dozen",
            name = "Classic Roses",
            price = 70.0,
            available = true
        )
        repository.moveToPickStage()
        repository.selectArrangement(rose)
        assertEquals(rose, repository.selectedArrangement.value)
        repository.moveToPayStage()
        // Trigger stale only on checkout re-selection (card_message options), not Pick.
        fakeApi.staleSelectionOnce = true
        val selectionsBeforeCheckout = fakeApi.selections.size
        repository.completeCheckout("card")
        assertEquals(JourneyStage.TRACKING, repository.currentStage.value)
        assertTrue(
            "checkout selection should have been retried once",
            fakeApi.selections.size >= selectionsBeforeCheckout + 2
        )
        assertNull(repository.errorMessage.value)
    }

    @Test
    fun bffExceptionMapsCodesToDistinctUserMessages() {
        assertTrue(
            BffException(409, "stale_context", "x").userMessage.contains("Workspace changed")
        )
        assertTrue(
            BffException(409, "total_mismatch", "x").userMessage.contains("total")
        )
        assertTrue(
            BffException(409, "checkout_conflict", "x").userMessage.contains("Checkout conflict")
        )
        assertTrue(
            BffException(409, "product_unavailable", "x").userMessage.contains("no longer available")
        )
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

    @Test
    fun budgetChipPatchesCorrectionAndFiltersLocalCatalog() = runBlocking {
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(
            contextVersion = 2,
            structuredIntent = StructuredIntent(occasion = "birthday")
        )
        repository.postUserMessage("birthday flowers")
        assertEquals("birthday", repository.sharedUnderstanding.value.occasion)
        assertFalse(repository.budgetPromptResolved.value)

        // Under $50 should keep Budget Mixed Bunch (35) and drop Classic Rose (70).
        repository.setBudgetChoice("Under $50", 50.0)
        assertTrue(repository.budgetPromptResolved.value)
        assertEquals("Under $50", repository.sharedUnderstanding.value.budget)
        assertEquals(1, fakeApi.corrections.size)
        assertTrue(fakeApi.corrections.last().corrections.containsKey("budget"))
        val skus = repository.arrangements.value.map { it.sku }
        assertTrue(skus.contains("budget-mixed-bunch"))
        assertFalse(skus.contains("classic-rose-dozen"))
        assertFalse(skus.contains("lilac-bouquet"))
    }

    @Test
    fun skipBudgetResolvesPromptWithoutCorrection() = runBlocking {
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(
            contextVersion = 2,
            structuredIntent = StructuredIntent(occasion = "birthday")
        )
        repository.postUserMessage("birthday")
        repository.skipBudget()
        assertTrue(repository.budgetPromptResolved.value)
        assertEquals("skipped", repository.sharedUnderstanding.value.budget)
        assertTrue(fakeApi.corrections.isEmpty())
        // Full catalog remains when skipped.
        assertTrue(repository.arrangements.value.size >= 3)
    }

    @Test
    fun liveBudgetInSharedUnderstandingResolvesPrompt() = runBlocking {
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(
            contextVersion = 3,
            structuredIntent = StructuredIntent(occasion = "anniversary", budget = "80")
        )
        repository.postUserMessage("Anniversary bouquet under $80")
        assertTrue(repository.budgetPromptResolved.value)
        assertEquals("80", repository.sharedUnderstanding.value.budget)
    }

    @Test
    fun parseBudgetCeilingFromLabelsAndNumbers() {
        assertEquals(50.0, SessionRepository.parseBudgetCeiling("Under $50")!!, 0.01)
        assertEquals(100.0, SessionRepository.parseBudgetCeiling("$50–100")!!, 0.01)
        assertNull(SessionRepository.parseBudgetCeiling("$100+"))
        assertNull(SessionRepository.parseBudgetCeiling("skipped"))
        assertEquals(75.0, SessionRepository.parseBudgetCeiling("75")!!, 0.01)
    }

    @Test
    fun budgetAsStringSerializerAcceptsJsonNumber() {
        val decoded = json.decodeFromString<StructuredIntent>("""{"occasion":"birthday","budget":75}""")
        assertEquals("75", decoded.budget)
        assertEquals("birthday", decoded.occasion)
    }

}

/** In-memory BFF stand-in for unit tests (no network). */
class FakeBffClient : BffClient() {
    var sharedUnderstanding: SharedUnderstandingResponse = SharedUnderstandingResponse()
    val postedMessages = mutableListOf<ConversationMessageRequest>()
    val corrections = mutableListOf<CorrectionRequest>()
    val selections = mutableListOf<SelectionRequest>()
    var orderPosted: Boolean = false
    var lastCheckout: CheckoutRequest? = null
    /** When true, first postSelection throws stale_context 409 then succeeds. */
    var staleSelectionOnce: Boolean = false
    /** When true, first postConversationMessage throws stale_context 409 then succeeds. */
    var staleConversationOnce: Boolean = false
    var clearSessionStateCalls: Int = 0
    var createSessionCalls: Int = 0
    /** True when the most recent createSession was preceded by clearSessionState. */
    var lastClearBeforeCreate: Boolean = false
    /** Ordered API touchpoints for contract ordering asserts (#367). */
    val callLog = mutableListOf<String>()
    /**
     * When true, postCheckout rejects observed_total that does not match
     * workspace order_summary.total after delivery (mirrors live total_mismatch).
     */
    var enforceOrderSummaryTotalOnCheckout: Boolean = false
    private var expectedCheckoutTotalOverride: Double? = null
    private var clearedSinceLastCreate: Boolean = false
    /** Test hook to bump fake server context version (mirrors private version). */
    var versionForTests: Int
        get() = version
        set(value) { version = value }
    private var version: Int = 0
    private var selectedPrice: Double = 70.0
    private var deliveryPosted: Boolean = false

    /** Force expected checkout total for isolated total_mismatch contract asserts. */
    fun setExpectedCheckoutTotalForTests(total: Double?) {
        expectedCheckoutTotalOverride = total
    }

    override fun clearSessionState() {
        clearSessionStateCalls += 1
        clearedSinceLastCreate = true
        callLog += "clearSessionState"
        super.clearSessionState()
    }

    override suspend fun createSession(): SessionCreateResponse {
        createSessionCalls += 1
        lastClearBeforeCreate = clearedSinceLastCreate
        clearedSinceLastCreate = false
        callLog += "createSession"
        version = 0
        deliveryPosted = false
        expectedCheckoutTotalOverride = null
        return SessionCreateResponse(csrfToken = "test-csrf")
    }

    override suspend fun postConversationMessage(
        messageText: String,
        observedContextVersion: Int
    ): AcceptedResponse {
        postedMessages += ConversationMessageRequest(messageText, observedContextVersion)
        if (staleConversationOnce) {
            staleConversationOnce = false
            version = observedContextVersion + 1
            throw BffException(
                statusCode = 409,
                errorCode = "stale_context",
                message = "BFF 409 stale_context",
                contextVersion = version
            )
        }
        version = observedContextVersion + 1
        return AcceptedResponse(accepted = true, code = "accepted", contextVersion = version)
    }

    override suspend fun getSharedUnderstanding(): SharedUnderstandingResponse {
        return sharedUnderstanding.copy(contextVersion = maxOf(sharedUnderstanding.contextVersion, version))
    }

    override suspend fun patchSharedUnderstanding(request: CorrectionRequest): AcceptedResponse {
        corrections += request
        version = request.observedContextVersion + 1
        val budgetEl = request.corrections["budget"] as? kotlinx.serialization.json.JsonPrimitive
        val budgetStr = budgetEl?.content
        val intent = sharedUnderstanding.structuredIntent
        sharedUnderstanding = sharedUnderstanding.copy(
            contextVersion = version,
            structuredIntent = intent.copy(
                budget = budgetStr ?: intent.budget
            )
        )
        return AcceptedResponse(accepted = true, code = "accepted", contextVersion = version)
    }

    override suspend fun getConversation(): ConversationResponse {
        return ConversationResponse(contextVersion = version, messages = emptyList())
    }

    override suspend fun getWorkspace(): WorkspaceResponse {
        val total = if (deliveryPosted) {
            selectedPrice + SessionRepository.REFERENCE_DELIVERY_FEE
        } else {
            null
        }
        return WorkspaceResponse(
            contextVersion = version,
            facets = WorkspaceFacets(
                orderSummary = total?.let { OrderSummaryFacet(total = it, currency = "USD") }
            )
        )
    }

    override suspend fun postSelection(request: SelectionRequest): AcceptedResponse {
        selections += request
        if (staleSelectionOnce) {
            staleSelectionOnce = false
            version = request.observedContextVersion + 1
            throw BffException(
                statusCode = 409,
                errorCode = "stale_context",
                message = "BFF 409 stale_context",
                contextVersion = version
            )
        }
        // Map known test SKUs to catalog-like prices for order_summary.
        selectedPrice = when (request.productId) {
            "classic-rose-dozen" -> 70.0
            "budget-mixed-bunch" -> 35.0
            "lilac-bouquet" -> 95.0
            else -> 70.0
        }
        version = request.observedContextVersion + 1
        return AcceptedResponse(accepted = true, code = "accepted", contextVersion = version)
    }

    override suspend fun postDelivery(request: DeliveryRequest): AcceptedResponse {
        deliveryPosted = true
        version = request.observedContextVersion + 1
        return AcceptedResponse(accepted = true, code = "accepted", contextVersion = version)
    }

    override suspend fun postOrder(): AcceptedResponse {
        orderPosted = true
        return AcceptedResponse(accepted = true, code = "accepted", orderId = "ord-test", status = "created")
    }

    override suspend fun postCheckout(request: CheckoutRequest): AcceptedResponse {
        callLog += "postCheckout"
        val expected = expectedCheckoutTotalOverride
            ?: if (deliveryPosted) selectedPrice + SessionRepository.REFERENCE_DELIVERY_FEE else null
        if (enforceOrderSummaryTotalOnCheckout && expected != null) {
            if (kotlin.math.abs(request.observedTotal - expected) > 0.01) {
                throw BffException(
                    statusCode = 409,
                    errorCode = "total_mismatch",
                    message = "BFF 409 total_mismatch",
                    contextVersion = version
                )
            }
        }
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
