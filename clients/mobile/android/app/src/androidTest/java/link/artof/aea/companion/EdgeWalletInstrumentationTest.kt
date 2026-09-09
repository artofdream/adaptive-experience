package link.artof.aea.companion

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import link.artof.aea.companion.data.wallet.EdgeWallet
import link.artof.aea.companion.data.wallet.EncryptedPrefsWalletStore
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

/**
 * #410 — device-backed list + clear. Needs an Android runtime (Keystore).
 * Not Play-honest prove; CI `android-build-debug` does not run connected tests.
 */
@RunWith(AndroidJUnit4::class)
class EdgeWalletInstrumentationTest {

    @Test
    fun encryptedStoreListsReceiptsThenClearEmptiesThem() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val wallet = EdgeWallet(EncryptedPrefsWalletStore(context))
        wallet.clear()

        wallet.saveReceipt(
            orderReference = "ord-instrumented",
            productId = "classic-rose-dozen",
            recipientLabel = "Mom",
        )
        val listed = wallet.receipts()
        assertEquals(1, listed.size)
        assertEquals("ord-instrumented", listed.first().orderReference)
        assertEquals("Mom", listed.first().recipientLabel)

        wallet.clear()
        assertTrue(wallet.receipts().isEmpty())
        assertEquals(null, wallet.latestReceipt())
    }
}
