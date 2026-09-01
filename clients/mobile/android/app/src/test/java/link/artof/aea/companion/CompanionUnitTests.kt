package link.artof.aea.companion

import link.artof.aea.companion.data.model.*
import link.artof.aea.companion.data.repository.JourneyStage
import link.artof.aea.companion.data.repository.SessionRepository
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class CompanionUnitTests {

    private lateinit var repository: SessionRepository
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }

    @Before
    fun setup() {
        repository = SessionRepository()
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
    fun testJourney1MessageUpdatesSharedUnderstanding() {
        repository.postUserMessage("I need flowers for Mom's birthday, same day delivery")
        val su = repository.sharedUnderstanding.value

        assertEquals("Mother's Birthday", su.occasion)
        assertEquals("Today (Same-Day)", su.deliveryDate)
        assertEquals("Mom", su.recipient)

        // Verify conversation contains assistant response
        val lastMsg = repository.messages.value.last()
        assertEquals("florist", lastMsg.sender)
        assertTrue(lastMsg.text.contains("roses", ignoreCase = true))
    }

    @Test
    fun testFailClosedUnavailableArrangementCannotBeSelected() {
        val soldOutArrangement = Arrangement(
            sku = "PEONY-SOLD-OUT",
            name = "Blush Peonies",
            price = 85.0,
            available = false
        )

        repository.selectArrangement(soldOutArrangement)
        assertNull(repository.selectedArrangement.value)
        assertNull(repository.sharedUnderstanding.value.selectedSku)
    }

    @Test
    fun testAvailableArrangementSelectionAndCheckout() {
        val rose = Arrangement(
            sku = "ROSE-01",
            name = "Classic Roses",
            price = 68.0,
            available = true
        )

        // 1. Move to Pick
        repository.moveToPickStage()
        assertEquals(JourneyStage.PICK, repository.currentStage.value)

        // 2. Select Arrangement
        repository.selectArrangement(rose)
        assertEquals(rose, repository.selectedArrangement.value)
        assertEquals("ROSE-01", repository.sharedUnderstanding.value.selectedSku)

        // 3. Move to Pay
        repository.moveToPayStage()
        assertEquals(JourneyStage.PAY, repository.currentStage.value)

        // 4. Complete Checkout
        repository.completeCheckout("Happy Birthday Mom!")
        assertEquals(JourneyStage.TRACKING, repository.currentStage.value)

        val order = repository.orderResult.value
        assertNotNull(order)
        assertEquals("CONFIRMED", order?.status)
        assertEquals(68.0, order?.totalAmount ?: 0.0, 0.01)
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
