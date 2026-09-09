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

    private val displayNames = mapOf(
        "classic-rose-dozen" to "Classic Rose Dozen",
        "lilac-bouquet" to "Lilac Bouquet",
        "budget-mixed-bunch" to "Budget Mixed Bunch",
        "pink-flower-vase" to "Pink Flower Vase",
        "premium-orchid" to "Premium Orchid",
    )

    fun imageUrlFor(sku: String?): String =
        bySku[sku?.trim().orEmpty()].orEmpty()

    /** Shopper-facing arrangement nickname for wallet review (not a street or PAN). */
    fun displayNameFor(sku: String?): String {
        val id = sku?.trim().orEmpty()
        if (id.isEmpty()) return "Arrangement"
        return displayNames[id] ?: id
    }
}
