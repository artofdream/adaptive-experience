package link.artof.aea.companion

import link.artof.aea.companion.data.wallet.EdgeWallet
import link.artof.aea.companion.data.wallet.InMemoryWalletStore
import link.artof.aea.companion.data.wallet.ReorderReference
import link.artof.aea.companion.data.wallet.WalletReceipt
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * ADR-020 Layer 2 Edge Wallet — pure-domain JVM tests. No Android runtime; the
 * encryption adapter (EncryptedPrefsWalletStore) is exercised under androidTest.
 */
class EdgeWalletTests {

    private fun wallet(initial: List<WalletReceipt> = emptyList(), now: Long = 1_000L): EdgeWallet {
        var t = now
        return EdgeWallet(InMemoryWalletStore(initial), clock = { t++ })
    }

    @Test
    fun savesAndReadsReceiptRoundTrip() {
        val w = wallet()
        w.saveReceipt(
            orderReference = "ord-1",
            productId = "budget-mixed-bunch",
            recipientLabel = "Mom",
            cardMessageDraft = "Happy Birthday!",
            occasionType = "Birthday",
            eventMonth = 9,
            eventDay = 10,
        )
        val receipts = w.receipts()
        assertEquals(1, receipts.size)
        val r = receipts.first()
        assertEquals("ord-1", r.orderReference)
        assertEquals("budget-mixed-bunch", r.productId)
        assertEquals("Mom", r.recipientLabel)
        assertEquals("Happy Birthday!", r.cardMessageDraft)
        assertEquals("birthday", r.occasionType) // normalized lower-case
        assertEquals(9, r.eventMonth)
        assertEquals(10, r.eventDay)
    }

    @Test
    fun latestReceiptIsMostRecentAndDedupsByOrderReference() {
        val w = wallet()
        w.saveReceipt(orderReference = "ord-1", productId = "classic-rose-dozen")
        w.saveReceipt(orderReference = "ord-2", productId = "lilac-bouquet")
        // Re-saving ord-1 must replace, not duplicate.
        w.saveReceipt(orderReference = "ord-1", productId = "premium-orchid")

        assertEquals(2, w.receipts().size)
        assertEquals("ord-1", w.latestReceipt()?.orderReference)
        assertEquals("premium-orchid", w.latestReceipt()?.productId)
    }

    @Test
    fun reorderReferenceExposesOnlyOpaqueIds_zeroPiiInvariant() {
        val w = wallet()
        w.saveReceipt(
            orderReference = "ord-42",
            productId = "classic-rose-dozen",
            recipientLabel = "Mum",
            cardMessageDraft = "With love, from Alex at 12 Rose Lane",
            occasionType = "anniversary",
        )
        val ref: ReorderReference = requireNotNull(w.reorderReference())

        assertEquals("classic-rose-dozen", ref.productId)
        assertEquals("ord-42", ref.orderReference)

        // Zero-PII invariant: the platform-facing type carries ONLY opaque ids —
        // no field can expose the device-only label / card / address.
        val fields = ReorderReference::class.java.declaredFields
            .map { it.name }
            .filterNot { it.startsWith("$") } // ignore synthetic
        assertEquals(setOf("productId", "orderReference"), fields.toSet())

        val rendered = ref.toString()
        assertTrue(rendered.contains("classic-rose-dozen"))
        assertTrue("must not leak recipient label", !rendered.contains("Mum"))
        assertTrue("must not leak card/address", !rendered.contains("Rose Lane"))
    }

    @Test
    fun reorderByExplicitOrderReferenceSelectsThatReceipt() {
        val w = wallet()
        w.saveReceipt(orderReference = "ord-1", productId = "classic-rose-dozen")
        w.saveReceipt(orderReference = "ord-2", productId = "lilac-bouquet")

        val ref = w.reorderReference("ord-1")
        assertEquals("classic-rose-dozen", ref?.productId)
    }

    @Test
    fun emptyWalletHasNoReorderReference() {
        assertNull(wallet().reorderReference())
        assertNull(wallet().latestReceipt())
    }

    @Test
    fun clearForgetsAllReceipts() {
        val w = wallet()
        w.saveReceipt(orderReference = "ord-1", productId = "classic-rose-dozen")
        w.clear()
        assertEquals(0, w.receipts().size)
        assertNull(w.reorderReference())
    }

    @Test
    fun blankOpaqueIdentifiersAreRejected() {
        val w = wallet()
        var threw = false
        try {
            w.saveReceipt(orderReference = "  ", productId = "classic-rose-dozen")
        } catch (e: IllegalArgumentException) {
            threw = true
        }
        assertTrue("blank orderReference must be rejected", threw)
    }
}
