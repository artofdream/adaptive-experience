package link.artof.aea.companion

import link.artof.aea.companion.data.wallet.WalletReceipt
import link.artof.aea.companion.data.wallet.WalletReview
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.concurrent.TimeUnit

/**
 * #410 — privacy-safe wallet review rows. JVM only; no Android runtime.
 */
class WalletReviewTests {

    private val now = 1_725_000_000_000L

    private fun receipt(
        order: String = "ord-42",
        sku: String = "classic-rose-dozen",
        recipient: String? = "Mom",
        card: String? = "Happy Birthday from 12 Rose Lane",
        savedAt: Long = now - TimeUnit.HOURS.toMillis(3),
    ) = WalletReceipt(
        orderReference = order,
        productId = sku,
        recipientLabel = recipient,
        cardMessageDraft = card,
        occasionType = "birthday",
        savedAtEpochMs = savedAt,
    )

    @Test
    fun reviewRowShowsRecipientNicknameOrderAndRelativeDate() {
        val row = WalletReview.row(receipt(), now)
        assertEquals("Mom", row.recipientLabel)
        assertEquals("Classic Rose Dozen", row.arrangementNickname)
        assertEquals("ord-42", row.orderReference)
        assertEquals("3 hours ago", row.relativeDate)
    }

    @Test
    fun blankRecipientFallsBackToSomeone() {
        assertEquals("Someone", WalletReview.row(receipt(recipient = "  "), now).recipientLabel)
        assertEquals("Someone", WalletReview.row(receipt(recipient = null), now).recipientLabel)
    }

    @Test
    fun reviewRowNeverExposesCardDraftStreetOrPan() {
        val row = WalletReview.row(
            receipt(card = "Visa 4111111111111111 at 12 Rose Lane"),
            now,
        )
        val rendered = listOf(
            row.recipientLabel,
            row.arrangementNickname,
            row.orderReference,
            row.relativeDate,
        ).joinToString(" ")
        assertFalse(rendered.contains("4111111111111111"))
        assertFalse(rendered.contains("Rose Lane"))
        assertFalse(rendered.contains("Happy Birthday"))
        assertFalse(rendered.contains("Visa"))
        val fields = row::class.java.declaredFields.map { it.name }.filterNot { it.startsWith("$") }
        assertEquals(
            setOf("recipientLabel", "arrangementNickname", "orderReference", "relativeDate"),
            fields.toSet(),
        )
    }

    @Test
    fun relativeDateBuckets() {
        assertEquals("Just now", WalletReview.relativeDate(now - 20_000L, now))
        assertEquals("1 minute ago", WalletReview.relativeDate(now - TimeUnit.MINUTES.toMillis(1), now))
        assertEquals("Yesterday", WalletReview.relativeDate(now - TimeUnit.DAYS.toMillis(1), now))
        assertEquals("3 days ago", WalletReview.relativeDate(now - TimeUnit.DAYS.toMillis(3), now))
        assertEquals("Unknown date", WalletReview.relativeDate(0L, now))
    }

    @Test
    fun rowsPreserveMostRecentFirstOrderFromCaller() {
        val rows = WalletReview.rows(
            listOf(
                receipt(order = "ord-new", savedAt = now),
                receipt(order = "ord-old", sku = "lilac-bouquet", recipient = "Mum", savedAt = now - 10_000L),
            ),
            now,
        )
        assertEquals(listOf("ord-new", "ord-old"), rows.map { it.orderReference })
        assertEquals("Lilac Bouquet", rows[1].arrangementNickname)
        assertEquals("Mum", rows[1].recipientLabel)
        assertTrue(WalletReview.EMPTY_TITLE.contains("No receipts"))
    }
}
