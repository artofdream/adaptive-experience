package link.artof.aea.companion.data.wallet

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

/**
 * ADR-020 Layer 2 at-rest storage: the device-owned Edge Wallet persisted in
 * [EncryptedSharedPreferences] under an Android Keystore master key (AES-256).
 *
 * This is the only Edge-Wallet file that depends on the Android runtime and
 * crypto; the [EdgeWallet] domain and its zero-PII logic stay pure Kotlin.
 * Device-only receipt fields (recipient label, card message) are encrypted at
 * rest here and, by construction of [ReorderReference], never leave the device.
 */
class EncryptedPrefsWalletStore(
    context: Context,
    private val json: Json = DEFAULT_JSON,
) : WalletStore {

    private val prefs by lazy {
        val appContext = context.applicationContext
        val masterKey = MasterKey.Builder(appContext)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        EncryptedSharedPreferences.create(
            appContext,
            PREFS_FILE,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
        )
    }

    override fun load(): List<WalletReceipt> {
        val blob = prefs.getString(KEY_RECEIPTS, null) ?: return emptyList()
        return try {
            json.decodeFromString<List<StoredReceipt>>(blob).map { it.toDomain() }
        } catch (_: Exception) {
            emptyList()
        }
    }

    override fun save(receipts: List<WalletReceipt>) {
        val blob = json.encodeToString(receipts.map { StoredReceipt.fromDomain(it) })
        prefs.edit().putString(KEY_RECEIPTS, blob).apply()
    }

    /** Serializable mirror so the pure-domain [WalletReceipt] needs no annotations. */
    @Serializable
    private data class StoredReceipt(
        val orderReference: String,
        val productId: String,
        val recipientLabel: String? = null,
        val cardMessageDraft: String? = null,
        val occasionType: String? = null,
        val eventMonth: Int? = null,
        val eventDay: Int? = null,
        val savedAtEpochMs: Long = 0L,
    ) {
        fun toDomain(): WalletReceipt = WalletReceipt(
            orderReference = orderReference,
            productId = productId,
            recipientLabel = recipientLabel,
            cardMessageDraft = cardMessageDraft,
            occasionType = occasionType,
            eventMonth = eventMonth,
            eventDay = eventDay,
            savedAtEpochMs = savedAtEpochMs,
        )

        companion object {
            fun fromDomain(r: WalletReceipt): StoredReceipt = StoredReceipt(
                orderReference = r.orderReference,
                productId = r.productId,
                recipientLabel = r.recipientLabel,
                cardMessageDraft = r.cardMessageDraft,
                occasionType = r.occasionType,
                eventMonth = r.eventMonth,
                eventDay = r.eventDay,
                savedAtEpochMs = r.savedAtEpochMs,
            )
        }
    }

    companion object {
        private const val PREFS_FILE = "aea_edge_wallet"
        private const val KEY_RECEIPTS = "receipts_v1"
        private val DEFAULT_JSON = Json { ignoreUnknownKeys = true; encodeDefaults = true }
    }
}
