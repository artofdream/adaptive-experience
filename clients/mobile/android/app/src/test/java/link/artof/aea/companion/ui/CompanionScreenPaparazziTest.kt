package link.artof.aea.companion.ui

import app.cash.paparazzi.DeviceConfig
import app.cash.paparazzi.Paparazzi
import link.artof.aea.companion.data.model.Arrangement
import link.artof.aea.companion.data.model.ChatMessage
import link.artof.aea.companion.data.model.SharedUnderstanding
import link.artof.aea.companion.ui.screens.NeedScreen
import link.artof.aea.companion.ui.screens.PayScreen
import link.artof.aea.companion.ui.screens.PickScreen
import link.artof.aea.companion.ui.theme.LilyCompanionTheme
import org.junit.Rule
import org.junit.Test

/**
 * Phase C (#364) — JVM Compose screenshots for Need / Pick / Pay.
 *
 * No emulator / Maestro. CI job `android-compose-screenshots` records PNGs as
 * artifacts (manual + allow_failure). Does **not** prove Play install or
 * dual-probe website/operator write-through (#360).
 */
class CompanionScreenPaparazziTest {

    @get:Rule
    val paparazzi = Paparazzi(
        deviceConfig = DeviceConfig.PIXEL_5,
        theme = "android:Theme.Material.Light.NoActionBar",
        maxPercentDifference = 0.01,
    )

    @Test
    fun needScreen_occasionUnlocked() {
        paparazzi.snapshot(name = "need_occasion_unlocked") {
            LilyCompanionTheme(darkTheme = false) {
                NeedScreen(
                    messages = sampleNeedMessages,
                    sharedUnderstanding = sampleUnderstanding,
                    onSendMessage = {},
                    onContinueToPick = {},
                    onStartOver = {},
                    isLoading = false,
                )
            }
        }
    }

    @Test
    fun pickScreen_withSelection() {
        paparazzi.snapshot(name = "pick_with_selection") {
            LilyCompanionTheme(darkTheme = false) {
                PickScreen(
                    arrangements = sampleArrangements,
                    selectedArrangement = sampleArrangements.first(),
                    quantity = 2,
                    onSelectArrangement = {},
                    onContinueToPay = {},
                    onBack = {},
                    onStartOver = {},
                    isLoading = false,
                )
            }
        }
    }

    @Test
    fun payScreen_checkoutSummary() {
        paparazzi.snapshot(name = "pay_checkout_summary") {
            LilyCompanionTheme(darkTheme = false) {
                PayScreen(
                    selectedArrangement = sampleArrangements.first(),
                    sharedUnderstanding = sampleUnderstanding,
                    onCheckout = {},
                    checkoutTotal = 89.0,
                    onBack = {},
                    onStartOver = {},
                    isLoading = false,
                )
            }
        }
    }

    companion object {
        // Fixed timestamps keep PNG diffs stable across runs.
        private val sampleNeedMessages = listOf(
            ChatMessage(
                id = "u1",
                sender = "user",
                text = "Anniversary bouquet under $80",
                timestamp = 1_725_000_000_000L,
            ),
            ChatMessage(
                id = "a1",
                sender = "florist",
                text = "Got it — anniversary, budget around \$80. Want same-day Paris delivery?",
                timestamp = 1_725_000_001_000L,
            ),
        )

        private val sampleUnderstanding = SharedUnderstanding(
            occasion = "Anniversary",
            recipient = "Partner",
            budget = "80",
            deliveryDate = "Today (Same-Day)",
            contextVersion = 2,
            stage = "need",
        )

        private val sampleArrangements = listOf(
            Arrangement(
                sku = "SKU-ANNIV-01",
                name = "Soft Anniversary Posy",
                price = 72.0,
                description = "Seasonal blush roses with eucalyptus.",
                available = true,
                tags = listOf("anniversary", "under-80"),
            ),
            Arrangement(
                sku = "SKU-ANNIV-02",
                name = "Classic Red Dozen",
                price = 78.0,
                description = "Twelve long-stem roses.",
                available = true,
                tags = listOf("anniversary"),
            ),
        )
    }
}
