package link.artof.aea.companion.ui.preview

import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.Preview
import link.artof.aea.companion.data.model.Arrangement
import link.artof.aea.companion.data.model.ChatMessage
import link.artof.aea.companion.data.model.SharedUnderstanding
import link.artof.aea.companion.ui.screens.NeedScreen
import link.artof.aea.companion.ui.screens.PayScreen
import link.artof.aea.companion.ui.screens.PickScreen
import link.artof.aea.companion.ui.theme.LilyCompanionTheme

/**
 * Studio @Preview surfaces for Need / Pick / Pay (#364 Phase C).
 * CI screenshots come from Paparazzi unit tests, not these previews alone.
 * Play internal remains the store-install honesty gate.
 */
private val previewMessages = listOf(
    ChatMessage(
        id = "u1",
        sender = "user",
        text = "Anniversary bouquet under $80",
        timestamp = 1_725_000_000_000L,
    ),
    ChatMessage(
        id = "a1",
        sender = "florist",
        text = "Got it — anniversary, budget around $80.",
        timestamp = 1_725_000_001_000L,
    ),
)

private val previewUnderstanding = SharedUnderstanding(
    occasion = "Anniversary",
    recipient = "Partner",
    budget = "80",
    deliveryDate = "Today (Same-Day)",
    contextVersion = 2,
    stage = "need",
)

private val previewArrangements = listOf(
    Arrangement(
        sku = "SKU-ANNIV-01",
        name = "Soft Anniversary Posy",
        price = 72.0,
        description = "Seasonal blush roses with eucalyptus.",
        available = true,
    ),
    Arrangement(
        sku = "SKU-ANNIV-02",
        name = "Classic Red Dozen",
        price = 78.0,
        description = "Twelve long-stem roses.",
        available = true,
    ),
)

@Preview(name = "Need — occasion unlocked", showBackground = true)
@Composable
fun NeedScreenPreview() {
    LilyCompanionTheme(darkTheme = false) {
        NeedScreen(
            messages = previewMessages,
            sharedUnderstanding = previewUnderstanding,
            onSendMessage = {},
            onContinueToPick = {},
            onStartOver = {},
        )
    }
}

@Preview(name = "Pick — with selection", showBackground = true)
@Composable
fun PickScreenPreview() {
    LilyCompanionTheme(darkTheme = false) {
        PickScreen(
            arrangements = previewArrangements,
            selectedArrangement = previewArrangements.first(),
            onSelectArrangement = {},
            onContinueToPay = {},
            onBack = {},
            onStartOver = {},
        )
    }
}

@Preview(name = "Pay — checkout summary", showBackground = true)
@Composable
fun PayScreenPreview() {
    LilyCompanionTheme(darkTheme = false) {
        PayScreen(
            selectedArrangement = previewArrangements.first(),
            sharedUnderstanding = previewUnderstanding,
            onCheckout = {},
            checkoutTotal = 89.0,
            onBack = {},
            onStartOver = {},
        )
    }
}
