package link.artof.aea.companion.data.wallet

import link.artof.aea.companion.data.model.CatalogArt
import java.util.concurrent.TimeUnit

/**
 * Privacy-safe Edge Wallet review rows (#410).
 *
 * Shoppers may see recipient label, arrangement nickname, opaque order ref,
 * and a relative date. Street address, card PAN, and card-message drafts stay
 * off this surface — they are not display fields here even when present on
 * the device-held [WalletReceipt].
 */
data class WalletReviewRow(
    val recipientLabel: String,
    val arrangementNickname: String,
    val orderReference: String,
    val relativeDate: String,
)

object WalletReview {
    const val UNKNOWN_RECIPIENT = "Someone"
    const val EMPTY_TITLE = "No receipts on this phone"
    const val EMPTY_BODY =
        "After you place an order, it is saved here — not in a Lily's Florist account. Need shows Reorder only when a receipt exists."
    const val CLEAR_CONFIRM_TITLE = "Clear History?"
    const val CLEAR_CONFIRM_BODY =
        "This deletes every encrypted receipt on this phone. The Need reorder card will disappear. Lily's Florist has no cloud copy of this list."

    fun rows(
        receipts: List<WalletReceipt>,
        nowEpochMs: Long = System.currentTimeMillis(),
    ): List<WalletReviewRow> = receipts.map { row(it, nowEpochMs) }

    fun row(
        receipt: WalletReceipt,
        nowEpochMs: Long = System.currentTimeMillis(),
    ): WalletReviewRow = WalletReviewRow(
        recipientLabel = recipientLabel(receipt.recipientLabel),
        arrangementNickname = CatalogArt.displayNameFor(receipt.productId),
        orderReference = receipt.orderReference,
        relativeDate = relativeDate(receipt.savedAtEpochMs, nowEpochMs),
    )

    fun recipientLabel(raw: String?): String =
        raw?.trim()?.ifEmpty { null } ?: UNKNOWN_RECIPIENT

    fun relativeDate(savedAtEpochMs: Long, nowEpochMs: Long): String {
        if (savedAtEpochMs <= 0L) return "Unknown date"
        val delta = nowEpochMs - savedAtEpochMs
        if (delta < 0L) return "Just now"
        val minutes = TimeUnit.MILLISECONDS.toMinutes(delta)
        val hours = TimeUnit.MILLISECONDS.toHours(delta)
        val days = TimeUnit.MILLISECONDS.toDays(delta)
        return when {
            minutes < 1L -> "Just now"
            minutes < 60L -> if (minutes == 1L) "1 minute ago" else "$minutes minutes ago"
            hours < 24L -> if (hours == 1L) "1 hour ago" else "$hours hours ago"
            days == 1L -> "Yesterday"
            days < 7L -> "$days days ago"
            else -> "$days days ago"
        }
    }
}
