package link.artof.aea.companion.data.wallet

/**
 * ADR-020 Layer 2 — the device-owned "Edge Wallet".
 *
 * The wallet keeps a customer's order history and reorder convenience data
 * ON THE DEVICE so returning-customer / FR-008 one-tap reorder works without
 * the platform holding a PII CRM (ADR-013 / NFR-017).
 *
 * Zero-PII boundary:
 * - [WalletReceipt.recipientLabel], [WalletReceipt.cardMessageDraft], and the
 *   occasion fields are DEVICE-ONLY convenience data. They never leave the
 *   device.
 * - Only opaque references ([ReorderReference]) are ever surfaced to the
 *   platform for a reorder. [ReorderReference] deliberately cannot carry a
 *   recipient label, card message, address, or payment detail.
 *
 * This class is pure Kotlin (no Android or serialization dependency) so the
 * reorder / zero-PII logic is unit-testable on the JVM. At-rest encryption is
 * provided by the [WalletStore] adapter (see EncryptedPrefsWalletStore).
 */
class EdgeWallet(
    private val store: WalletStore,
    private val clock: () -> Long = { System.currentTimeMillis() },
) {
    /**
     * Record a completed order as a device-held receipt. Idempotent per
     * [orderReference] (a re-save for the same opaque order id replaces the
     * prior entry rather than duplicating it).
     */
    fun saveReceipt(
        orderReference: String,
        productId: String,
        recipientLabel: String? = null,
        cardMessageDraft: String? = null,
        occasionType: String? = null,
        eventMonth: Int? = null,
        eventDay: Int? = null,
    ): WalletReceipt {
        val order = orderReference.trim()
        val product = productId.trim()
        require(order.isNotEmpty()) { "orderReference is required" }
        require(product.isNotEmpty()) { "productId is required" }

        val receipt = WalletReceipt(
            orderReference = order,
            productId = product,
            recipientLabel = recipientLabel?.trim()?.ifEmpty { null },
            cardMessageDraft = cardMessageDraft?.trim()?.ifEmpty { null },
            occasionType = occasionType?.trim()?.lowercase()?.ifEmpty { null },
            eventMonth = eventMonth?.takeIf { it in 1..12 },
            eventDay = eventDay?.takeIf { it in 1..31 },
            savedAtEpochMs = clock(),
        )
        val retained = store.load().filterNot { it.orderReference == order }
        store.save(retained + receipt)
        return receipt
    }

    /** All device-held receipts, most recent first. */
    fun receipts(): List<WalletReceipt> =
        store.load().sortedByDescending { it.savedAtEpochMs }

    /** The most recent receipt, or null when the wallet is empty. */
    fun latestReceipt(): WalletReceipt? = receipts().firstOrNull()

    /**
     * Opaque-only payload for an FR-008 reorder. When [orderReference] is null
     * the latest receipt is used. Returns null when there is nothing to reorder.
     *
     * The returned [ReorderReference] carries ONLY the opaque product and order
     * ids — never the recipient label, card message, or any PII — so the caller
     * cannot accidentally leak device-only data to the platform.
     */
    fun reorderReference(orderReference: String? = null): ReorderReference? {
        val receipt = if (orderReference == null) {
            latestReceipt()
        } else {
            receipts().firstOrNull { it.orderReference == orderReference.trim() }
        } ?: return null
        return ReorderReference(
            productId = receipt.productId,
            orderReference = receipt.orderReference,
        )
    }

    /** Forget all device-held history (customer erasure / sign-out). */
    fun clear() = store.save(emptyList())
}

/**
 * A device-held order receipt. Fields marked device-only are ADR-020 Layer-2
 * convenience data and must never be sent to the platform.
 */
data class WalletReceipt(
    /** Opaque platform order id (safe to present to the platform). */
    val orderReference: String,
    /** Opaque catalog SKU (safe to present to the platform). */
    val productId: String,
    /** Device-only. e.g. "Mom". Never leaves the device. */
    val recipientLabel: String? = null,
    /** Device-only. Never leaves the device. */
    val cardMessageDraft: String? = null,
    /** Device-only convenience for local reminders. */
    val occasionType: String? = null,
    /** Device-only convenience for local reminders. */
    val eventMonth: Int? = null,
    /** Device-only convenience for local reminders. */
    val eventDay: Int? = null,
    val savedAtEpochMs: Long = 0L,
)

/**
 * The ONLY shape the Edge Wallet exposes toward the platform for a reorder.
 * Opaque references only — structurally incapable of carrying PII.
 */
data class ReorderReference(
    val productId: String,
    val orderReference: String,
)

/**
 * Persistence port for the Edge Wallet. Implementations own encryption at rest
 * and serialization; the [EdgeWallet] domain stays free of Android/crypto deps.
 */
interface WalletStore {
    fun load(): List<WalletReceipt>
    fun save(receipts: List<WalletReceipt>)
}

/**
 * In-memory [WalletStore]. Used as the safe default when no encrypted
 * device-backed store is provided (and in unit tests). Not persisted.
 */
class InMemoryWalletStore(initial: List<WalletReceipt> = emptyList()) : WalletStore {
    private var data: List<WalletReceipt> = initial.toList()
    override fun load(): List<WalletReceipt> = data
    override fun save(receipts: List<WalletReceipt>) {
        data = receipts.toList()
    }
}
