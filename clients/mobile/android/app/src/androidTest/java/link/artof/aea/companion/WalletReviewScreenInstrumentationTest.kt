package link.artof.aea.companion

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import link.artof.aea.companion.data.wallet.WalletReceipt
import link.artof.aea.companion.data.wallet.WalletReview
import link.artof.aea.companion.ui.screens.WalletReviewScreen
import link.artof.aea.companion.ui.theme.LilyCompanionTheme
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * #410 — Compose instrumentation: list a receipt, confirm Clear History, empty state.
 * Not Play-honest prove. Requires a connected device/emulator.
 */
@RunWith(AndroidJUnit4::class)
class WalletReviewScreenInstrumentationTest {

    @get:Rule
    val compose = createComposeRule()

    @Test
    fun listsReceiptThenConfirmedClearShowsEmptyState() {
        var cleared = false
        val now = 1_725_000_000_000L
        val receipt = WalletReceipt(
            orderReference = "ord-ui",
            productId = "classic-rose-dozen",
            recipientLabel = "Mom",
            cardMessageDraft = "Visa 4111111111111111",
            savedAtEpochMs = now - 3_600_000L,
        )

        compose.setContent {
            var receipts by remember { mutableStateOf(listOf(receipt)) }
            LilyCompanionTheme(darkTheme = false) {
                WalletReviewScreen(
                    receipts = receipts,
                    onClose = {},
                    onClearHistory = {
                        cleared = true
                        receipts = emptyList()
                    },
                    nowEpochMs = now,
                )
            }
        }

        compose.onNodeWithText("For Mom").assertExists()
        compose.onNodeWithText("Classic Rose Dozen").assertExists()
        compose.onNodeWithText("Order ord-ui").assertExists()
        compose.onNodeWithText("Visa 4111111111111111").assertDoesNotExist()
        compose.onNodeWithText("Clear History").performClick()
        compose.onNodeWithText(WalletReview.CLEAR_CONFIRM_TITLE).assertExists()
        compose.onAllNodesWithText("Clear History")[1].performClick()
        compose.onNodeWithText(WalletReview.EMPTY_TITLE).assertExists()
        assertTrue(cleared)
    }
}
