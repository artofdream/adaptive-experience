package link.artof.aea.companion.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.layout.Arrangement
import link.artof.aea.companion.data.model.Arrangement as FloristArrangement
import link.artof.aea.companion.data.repository.JourneyStage
import link.artof.aea.companion.ui.theme.*
import coil.compose.AsyncImage

@Composable
fun StageProgressBar(
    currentStage: JourneyStage,
    modifier: Modifier = Modifier
) {
    val stages = listOf(
        JourneyStage.NEED to "1. Need",
        JourneyStage.PICK to "2. Pick",
        JourneyStage.PAY to "3. Pay"
    )

    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        stages.forEach { (stage, label) ->
            val isActive = currentStage == stage
            val isCompleted = currentStage.ordinal > stage.ordinal
            
            val bgColor = when {
                isActive -> MaterialTheme.colorScheme.primary
                isCompleted -> MaterialTheme.colorScheme.secondary.copy(alpha = 0.3f)
                else -> MaterialTheme.colorScheme.surface
            }
            val textColor = when {
                isActive -> MaterialTheme.colorScheme.onPrimary
                else -> MaterialTheme.colorScheme.onBackground
            }

            Box(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(16.dp))
                    .background(bgColor)
                    .border(
                        1.dp,
                        if (isActive) MaterialTheme.colorScheme.primary else Color.Transparent,
                        RoundedCornerShape(16.dp)
                    )
                    .padding(vertical = 8.dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = label,
                    color = textColor,
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = if (isActive) FontWeight.Bold else FontWeight.Normal
                )
            }
        }
    }
}

@Composable
fun ChatBubble(
    sender: String,
    text: String,
    modifier: Modifier = Modifier
) {
    val isUser = sender == "user"
    val align = if (isUser) Alignment.End else Alignment.Start
    val bgColor = if (isUser) MaterialTheme.colorScheme.primary.copy(alpha = 0.15f) else MaterialTheme.colorScheme.surface
    val borderColor = if (isUser) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant

    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        horizontalAlignment = align
    ) {
        Box(
            modifier = Modifier
                .widthIn(max = 280.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(bgColor)
                .border(1.dp, borderColor, RoundedCornerShape(12.dp))
                .padding(12.dp)
        ) {
            Text(
                text = text,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onBackground
            )
        }
    }
}

@Composable
fun ArrangementCard(
    arrangement: FloristArrangement,
    isSelected: Boolean,
    onSelect: () -> Unit,
    modifier: Modifier = Modifier
) {
    val borderColor = when {
        isSelected -> MaterialTheme.colorScheme.primary
        arrangement.available -> MaterialTheme.colorScheme.surfaceVariant
        else -> MaterialTheme.colorScheme.error.copy(alpha = 0.5f)
    }

    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 6.dp)
            .clickable(enabled = arrangement.available) { onSelect() },
        shape = RoundedCornerShape(14.dp),
        elevation = CardDefaults.cardElevation(
            defaultElevation = if (isSelected) 4.dp else 1.dp
        ),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) MaterialTheme.colorScheme.primary.copy(alpha = 0.12f) else MaterialTheme.colorScheme.surface
        ),
        border = CardDefaults.outlinedCardBorder().copy(
            brush = androidx.compose.ui.graphics.SolidColor(borderColor),
            width = if (isSelected) 2.dp else 1.dp
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            if (arrangement.imageUrl.isNotBlank()) {
                AsyncImage(
                    model = arrangement.imageUrl,
                    contentDescription = arrangement.name,
                    contentScale = ContentScale.Crop,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(140.dp)
                        .clip(RoundedCornerShape(10.dp))
                )
                Spacer(modifier = Modifier.height(12.dp))
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = arrangement.name,
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.weight(1f)
                )
                Text(
                    text = "$${"%.2f".format(arrangement.price)}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = arrangement.description,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f)
            )

            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Availability badge (NFR-009)
                val badgeText = if (arrangement.available) "Available Today" else "Sold Out"
                val badgeColor = if (arrangement.available) AvailableGreen else UnavailableRed

                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(6.dp))
                        .background(badgeColor.copy(alpha = 0.15f))
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = badgeText,
                        color = badgeColor,
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                }

                if (isSelected) {
                    Text(
                        text = "Selected ✓",
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold,
                        style = MaterialTheme.typography.labelMedium
                    )
                }
            }
        }
    }
}

@Composable
fun QuantityStepper(
    quantity: Int,
    onQuantityChange: (Int) -> Unit,
    enabled: Boolean = true,
    modifier: Modifier = Modifier,
    min: Int = 1,
    max: Int = 10,
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = "Quantity",
            style = MaterialTheme.typography.titleSmall,
            color = MaterialTheme.colorScheme.onBackground
        )
        Row(verticalAlignment = Alignment.CenterVertically) {
            OutlinedButton(
                onClick = { onQuantityChange((quantity - 1).coerceAtLeast(min)) },
                enabled = enabled && quantity > min,
                modifier = Modifier.size(width = 48.dp, height = 40.dp),
                contentPadding = PaddingValues(0.dp)
            ) {
                Text("−")
            }
            Text(
                text = quantity.toString(),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(horizontal = 16.dp)
            )
            OutlinedButton(
                onClick = { onQuantityChange((quantity + 1).coerceAtMost(max)) },
                enabled = enabled && quantity < max,
                modifier = Modifier.size(width = 48.dp, height = 40.dp),
                contentPadding = PaddingValues(0.dp)
            ) {
                Text("+")
            }
        }
    }
}

@Composable
fun AsoDisclaimer(
    modifier: Modifier = Modifier
) {
    Text(
        text = "This is an automated florist assistant, not a person (FR-009).",
        style = MaterialTheme.typography.labelMedium.copy(fontSize = 11.sp),
        color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.6f),
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 6.dp)
    )
}
