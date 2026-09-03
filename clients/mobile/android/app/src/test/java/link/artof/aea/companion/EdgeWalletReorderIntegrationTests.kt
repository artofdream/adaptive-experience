package link.artof.aea.companion

import link.artof.aea.companion.data.model.Arrangement
import link.artof.aea.companion.data.model.SharedUnderstandingResponse
import link.artof.aea.companion.data.model.StructuredIntent
import link.artof.aea.companion.data.repository.JourneyStage
import link.artof.aea.companion.data.repository.SessionRepository
import link.artof.aea.companion.data.wallet.EdgeWallet
import link.artof.aea.companion.data.wallet.InMemoryWalletStore
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

/**
 * ADR-020 Layer 2 — repository wiring: a confirmed checkout writes a device-held
 * Edge Wallet receipt, and FR-008 reorder re-selects the opaque product id.
 */
class EdgeWalletReorderIntegrationTests {

    private lateinit var fakeApi: FakeBffClient
    private lateinit var store: InMemoryWalletStore
    private lateinit var wallet: EdgeWallet
    private lateinit var repository: SessionRepository

    @Before
    fun setup() {
        fakeApi = FakeBffClient()
        store = InMemoryWalletStore()
        wallet = EdgeWallet(store)
        repository = SessionRepository(api = fakeApi, wallet = wallet)
    }

    private val rose = Arrangement(
        sku = "classic-rose-dozen",
        name = "Classic Roses",
        price = 70.0,
        available = true,
    )

    @Test
    fun confirmedCheckoutWritesDeviceReceiptWithoutPlatformPii() = runBlocking {
        // Recipient label "Mum" is a DEVICE-ONLY wallet field. It is a distinct
        // token from the physical card message (which the T-04 / ADR-006 contract
        // intentionally does send to the platform), so this test can prove the
        // label itself never leaves the device.
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(
            contextVersion = 2,
            structuredIntent = StructuredIntent(occasion = "birthday", recipient = "Mum"),
        )
        repository.postUserMessage("birthday flowers")
        repository.moveToPickStage()
        repository.selectArrangement(rose)
        repository.moveToPayStage()
        repository.completeCheckout("Happy Birthday!")

        assertEquals(JourneyStage.TRACKING, repository.currentStage.value)
        // One device-held receipt written for the confirmed order.
        assertEquals(1, repository.walletReceiptCount())
        val receipt = wallet.latestReceipt()!!
        assertEquals("classic-rose-dozen", receipt.productId)
        assertEquals("Mum", receipt.recipientLabel)      // device-only
        assertEquals("Happy Birthday!", receipt.cardMessageDraft) // device-only
        assertEquals("birthday", receipt.occasionType)

        // The opaque reorder reference carries no recipient/card/PII.
        val ref = repository.walletReorderReference()!!
        assertEquals("classic-rose-dozen", ref.productId)
        assertFalse(ref.toString().contains("Mum"))

        // Zero-PII invariant: the device-only recipient label never crosses to
        // the platform — not as a selection option value, nor as a recipient key.
        // (The physical card message is a separate, intended T-04 field.)
        assertTrue(fakeApi.selections.none { sel -> sel.options.values.any { it.contains("Mum") } })
        assertTrue(fakeApi.selections.none { sel ->
            sel.options.keys.any { it == "recipient" || it == "recipient_label" }
        })
    }

    @Test
    fun reorderFromWalletReselectsStoredOpaqueProduct() = runBlocking {
        fakeApi.sharedUnderstanding = SharedUnderstandingResponse(contextVersion = 2)
        repository.moveToPickStage()
        repository.selectArrangement(rose)
        repository.moveToPayStage()
        repository.completeCheckout("card")
        val selectionsAfterCheckout = fakeApi.selections.size

        val reordered = repository.reorderFromWallet()
        assertTrue("reorder should succeed when wallet has a receipt", reordered)
        assertEquals(JourneyStage.PICK, repository.currentStage.value)
        assertTrue(
            "reorder must POST a selection for the stored opaque product id",
            fakeApi.selections.size > selectionsAfterCheckout,
        )
        assertEquals("classic-rose-dozen", fakeApi.selections.last().productId)
        assertEquals("classic-rose-dozen", repository.sharedUnderstanding.value.selectedSku)
    }

    @Test
    fun reorderFromEmptyWalletReturnsFalse() = runBlocking {
        assertFalse(repository.reorderFromWallet())
        assertNull(repository.walletReorderReference())
        assertTrue(fakeApi.selections.isEmpty())
    }
}
