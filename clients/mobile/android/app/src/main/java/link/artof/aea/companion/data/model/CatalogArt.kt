package link.artof.aea.companion.data.model

/**
 * Public SKU art already shipped for the web shop (`PRODUCT_ART` in app.js).
 * Companion mirrors the same Path B assets — no CMS, no new photography (#397).
 */
object CatalogArt {
    private const val BASE = "https://aea.artof.link/assets"

    private val bySku = mapOf(
        "classic-rose-dozen" to "$BASE/sku-classic-rose-dozen.jpg",
        "lilac-bouquet" to "$BASE/sku-lilac-bouquet.jpg",
        "budget-mixed-bunch" to "$BASE/sku-budget-mixed-bunch.jpg",
        "pink-flower-vase" to "$BASE/sku-pink-flower-vase.jpg",
        "premium-orchid" to "$BASE/sku-premium-orchid.jpg",
    )

    fun imageUrlFor(sku: String?): String =
        bySku[sku?.trim().orEmpty()].orEmpty()
}
