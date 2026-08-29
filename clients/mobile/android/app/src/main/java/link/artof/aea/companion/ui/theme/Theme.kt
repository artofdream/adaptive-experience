package link.artof.aea.companion.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = AccentGoldDark,
    onPrimary = SandDark,
    background = SandDark,
    onBackground = CharcoalDark,
    surface = CardBackgroundDark,
    onSurface = CharcoalDark,
    secondary = LinkBlue,
    error = WarnAmber
)

private val LightColorScheme = lightColorScheme(
    primary = AccentGold,
    onPrimary = SandLight,
    background = SandLight,
    onBackground = CharcoalLight,
    surface = CardBackgroundLight,
    onSurface = CharcoalLight,
    secondary = LinkBlue,
    error = WarnAmber
)

@Composable
fun LilyCompanionTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
