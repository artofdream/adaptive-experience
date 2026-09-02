package link.artof.aea.companion

import link.artof.aea.companion.data.api.BffClient
import link.artof.aea.companion.data.model.Arrangement
import link.artof.aea.companion.data.model.BffException
import link.artof.aea.companion.data.model.CheckoutRequest
import link.artof.aea.companion.data.model.SharedUnderstandingResponse
import link.artof.aea.companion.data.model.WorkspaceResponse
import link.artof.aea.companion.data.repository.JourneyStage
import link.artof.aea.companion.data.repository.SessionRepository
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.double
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Before
import org.junit.Test

/**
 * Native↔web BFF contract tests (#367).
 *
 * Golden fixtures under `src/test/resources/bff_golden/` mirror web
 * `confirmAndPay` (edge/gateway/ui/assets/app.js): checkout posts
 * `observed_total = Number(order_summary.total)` after delivery fee, not
 * product-only price. Start Over must clearSessionState before createSession
 * (!380 / #366).
 *
 * These regressions would fail on pre-!379 (product-only observed_total →
 * total_mismatch) and pre-!380 (Start Over without cookie clear).
 * Does **not** close #360 (dual-probe honesty).
 */
class BffWebContractTests {

    private lateinit var fakeApi: FakeBffClient
    private lateinit var repository: SessionRepository
    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        encodeDefaults = true
        explicitNulls = false
    }

    @Before
    fun setup() {
        fakeApi = FakeBffClient()
        // Enforce BFF total_mismatch when checkout drifts from order_summary.
        fakeApi.enforceOrderSummaryTotalOnCheckout = true
        repository = SessionRepository(api = fakeApi)
    }

    private fun loadGolden(name: String): String {
        val stream = javaClass.classLoader!!.getResourceAsStream("bff_golden/$name")
            ?: error("Missing golden fixture bff_golden/$name")
        return stream.bufferedReader().use { it.readText() }
    }

    @Test
    fun goldenWorkspaceAfterDeliveryMatchesWebOrderSummaryShape() {
        val golden = json.parseToJsonElement(loadGolden("workspace_after_delivery.json")).jsonObject
        val summary = golden["facets"]!!.jsonObject["order_summary"]!!.jsonObject
        assertEquals(82.0, summary["total"]!!.jsonPrimitive.double, 0.01)
        assertEquals("USD", summary["currency"]!!.jsonPrimitive.content)

        val decoded = json.decodeFromString<WorkspaceResponse>(loadGolden("workspace_after_delivery.json"))
        assertEquals(6, decoded.contextVersion)
        assertEquals(82.0, decoded.facets.orderSummary!!.total!!, 0.01)

        // Product-only (pre-!379 bug) is NOT the web golden total for $70 roses + $12 fee.
        assertFalse(
            "Golden total must include REFERENCE_DELIVERY_FEE, not product-only 70",
            decoded.facets.orderSummary!!.total == 70.0
        )
        assertEquals(
            70.0 + SessionRepository.REFERENCE_DELIVERY_FEE,
            decoded.facets.orderSummary!!.total!!,
            0.01
        )
    }

    @Test
    fun goldenCheckoutRequestMatchesWebConfirmAndPayBody() {
        val golden = json.parseToJsonElement(loadGolden("checkout_request_web_shape.json")).jsonObject
        assertEquals("session_pay_ref", golden["payment_reference"]!!.jsonPrimitive.content)
        assertEquals(82.0, golden["observed_total"]!!.jsonPrimitive.double, 0.01)
        assertFalse(golden.containsKey("card_number"))
        assertFalse(golden.containsKey("session_token"))

        val decoded = json.decodeFromString<CheckoutRequest>(loadGolden("checkout_request_web_shape.json"))
        assertEquals(BffClient.SESSION_PAYMENT_REFERENCE, decoded.paymentReference)
        assertEquals(82.0, decoded.observedTotal, 0.01)

        // Kotlin model serializes to the same snake_case keys web posts.
        val encoded = json.encodeToString(decoded)
        assertTrue(encoded.contains("\"payment_reference\""))
        assertTrue(encoded.contains("\"observed_total\""))
        assertTrue(encoded.contains("82"))
    }

    @Test
    fun checkoutObservedTotalUsesWorkspaceOrderSummaryNotProductOnly() = runBlocking {
        // Regression for pre-!379: product-only observed_total → BFF total_mismatch 409.
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
        assertNotNull(fakeApi.lastCheckout)
        val posted = fakeApi.lastCheckout!!

        val goldenCheckout = json.decodeFromString<CheckoutRequest>(
            loadGolden("checkout_request_web_shape.json")
        )
        assertEquals(
            "Must mirror web confirmAndPay observed_total from order_summary.total",
            goldenCheckout.observedTotal,
            posted.observedTotal,
            0.01
        )
        assertEquals(goldenCheckout.paymentReference, posted.paymentReference)
        assertEquals(
            70.0 + SessionRepository.REFERENCE_DELIVERY_FEE,
            posted.observedTotal,
            0.01
        )
        assertFalse(
            "Product-only observed_total is the pre-!379 drift class",
            posted.observedTotal == rose.price
        )
        assertEquals(82.0, repository.orderSummaryTotal.value ?: 0.0, 0.01)
        assertEquals(null, repository.errorMessage.value)
    }

    @Test
    fun productOnlyObservedTotalWouldTotalMismatchAgainstGoldenWorkspace() {
        // Documents the BFF contract: FakeBffClient rejects product-only like live edge.
        val goldenWorkspace = json.decodeFromString<WorkspaceResponse>(
            loadGolden("workspace_after_delivery.json")
        )
        val summaryTotal = goldenWorkspace.facets.orderSummary!!.total!!
        val productOnly = 70.0
        assertTrue(summaryTotal > productOnly)

        fakeApi.enforceOrderSummaryTotalOnCheckout = true
        fakeApi.setExpectedCheckoutTotalForTests(summaryTotal)
        try {
            runBlocking {
                fakeApi.postCheckout(
                    CheckoutRequest(
                        paymentReference = BffClient.SESSION_PAYMENT_REFERENCE,
                        observedTotal = productOnly
                    )
                )
            }
            fail("Expected total_mismatch 409 for product-only observed_total")
        } catch (ex: BffException) {
            assertEquals(409, ex.statusCode)
            assertEquals("total_mismatch", ex.errorCode)
        }
    }

    @Test
    fun startOverClearsSessionCookiesBeforeCreateSession() = runBlocking {
        // Regression for pre-!380: Start Over without clearSessionState reused
        // __Host-aea_* cookies and next Need posted observed_context_version:0
        // against the old live session (stale_context).
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(contextVersion = 3)
        repository.ensureSession()
        assertTrue(repository.sessionReady.value)

        fakeApi.clearSessionStateCalls = 0
        fakeApi.createSessionCalls = 0
        fakeApi.callLog.clear()

        repository.startOver()

        assertEquals(1, fakeApi.clearSessionStateCalls)
        assertEquals(1, fakeApi.createSessionCalls)
        assertTrue(
            "clearSessionState must precede createSession on Start Over (#366 / !380)",
            fakeApi.lastClearBeforeCreate
        )
        val clearIdx = fakeApi.callLog.indexOf("clearSessionState")
        val createIdx = fakeApi.callLog.indexOf("createSession")
        assertTrue(clearIdx >= 0)
        assertTrue(createIdx >= 0)
        assertTrue(
            "call order: clearSessionState before createSession, got ${fakeApi.callLog}",
            clearIdx < createIdx
        )
        assertEquals(JourneyStage.NEED, repository.currentStage.value)
        assertTrue(repository.sessionReady.value)
    }

    @Test
    fun webConfirmAndPayContractCommentMatchesCompanionPath() {
        // Sanity: companion constants stay aligned with web app.js SESSION_* refs.
        assertEquals("session_pay_ref", BffClient.SESSION_PAYMENT_REFERENCE)
        assertEquals("home", BffClient.SESSION_DESTINATION_REFERENCE)
        assertEquals(12.0, SessionRepository.REFERENCE_DELIVERY_FEE, 0.01)
        // Golden fixture total for classic-rose-dozen ($70) + fee.
        assertEquals(
            82.0,
            70.0 + SessionRepository.REFERENCE_DELIVERY_FEE,
            0.01
        )
    }
}
