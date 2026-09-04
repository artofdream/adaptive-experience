package link.artof.aea.companion.data.model

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CatalogArtTest {
    @Test
    fun knownSkuMapsToPublicAsset() {
        val url = CatalogArt.imageUrlFor("lilac-bouquet")
        assertTrue(url.startsWith("https://aea.artof.link/assets/"))
        assertTrue(url.endsWith("sku-lilac-bouquet.jpg"))
    }

    @Test
    fun unknownSkuIsBlank() {
        assertEquals("", CatalogArt.imageUrlFor("not-a-sku"))
        assertEquals("", CatalogArt.imageUrlFor(null))
    }
}
