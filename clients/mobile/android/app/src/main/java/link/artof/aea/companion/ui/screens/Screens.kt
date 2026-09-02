package link.artof.aea.companion.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.layout.Arrangement
import link.artof.aea.companion.data.model.Arrangement as FloristArrangement
import link.artof.aea.companion.data.model.ChatMessage
import link.artof.aea.companion.data.model.OrderResult
import link.artof.aea.companion.data.model.SharedUnderstanding
import link.artof.aea.companion.ui.components.*

@Composable
fun NeedScreen(
    messages: List<ChatMessage>,
    sharedUnderstanding: SharedUnderstanding,
    onSendMessage: (String) -> Unit,
    onContinueToPick: () -> Unit,
    onStartOver: (() -> Unit)? = null,
    isLoading: Boolean = false,
    modifier: Modifier = Modifier
) {
    var inputText by remember { mutableStateOf("") }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(bottom = 16.dp)
    ) {
        AsoDisclaimer()

        // Conversation history
        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
        ) {
            items(messages) { msg ->
                ChatBubble(sender = msg.sender, text = msg.text)
            }
        }

        // Quick Suggestion Chips (J1 Urgent Sam shortcut)
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 4.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            SuggestionChip(
                onClick = { onSendMessage("I need flowers for Mom\'s birthday, same day") },
                label = { Text("Mom\'s Birthday (Same-Day)") }
            )
            SuggestionChip(
                onClick = { onSendMessage("Anniversary bouquet under $80") },
                label = { Text("Anniversary ($80)") }
            )
        }

        // Text input row
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = inputText,
                onValueChange = { inputText = it },
                placeholder = { Text("Tell Lily what you need...") },
                modifier = Modifier.weight(1f),
                maxLines = 2
            )
            Spacer(modifier = Modifier.width(8.dp))
            Button(
                onClick = {
                    if (inputText.isNotBlank()) {
                        onSendMessage(inputText)
                        inputText = ""
                    }
                },
                enabled = !isLoading,
                modifier = Modifier.height(56.dp)
            ) {
                Text("Send")
            }
        }

        // Primary Single CTA (UX Rule: exactly one primary CTA per stage)
        val hasOccasion = !sharedUnderstanding.occasion.isNullOrEmpty()
        Button(
            onClick = onContinueToPick,
            enabled = hasOccasion && !isLoading,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 4.dp)
                .height(52.dp)
        ) {
            Text(if (hasOccasion) "View Arrangements (${sharedUnderstanding.occasion}) →" else "Specify Occasion to Continue")
        }

        if (onStartOver != null) {
            TextButton(
                onClick = onStartOver,
                enabled = !isLoading,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp)
            ) {
                Text("Start Over")
            }
        }
    }
}

@Composable
fun PickScreen(
    arrangements: List<FloristArrangement>,
    selectedArrangement: FloristArrangement?,
    onSelectArrangement: (FloristArrangement) -> Unit,
    onContinueToPay: () -> Unit,
    onBack: (() -> Unit)? = null,
    onStartOver: (() -> Unit)? = null,
    isLoading: Boolean = false,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(bottom = 16.dp)
    ) {
        AsoDisclaimer()

        Text(
            text = "Recommended Arrangements",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
        )

        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
        ) {
            items(arrangements) { arrangement ->
                ArrangementCard(
                    arrangement = arrangement,
                    isSelected = selectedArrangement?.sku == arrangement.sku,
                    onSelect = { onSelectArrangement(arrangement) }
                )
            }
        }

        // Primary Single CTA
        Button(
            onClick = onContinueToPay,
            enabled = selectedArrangement != null && !isLoading,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 4.dp)
                .height(52.dp)
        ) {
            Text(
                if (selectedArrangement != null)
                    "Continue to Checkout ($${"%.2f".format(selectedArrangement.price)}) →"
                else
                    "Select an Arrangement to Continue"
            )
        }

        if (onBack != null) {
            OutlinedButton(
                onClick = onBack,
                enabled = !isLoading,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 2.dp)
            ) {
                Text("← Back to Need")
            }
        }
        if (onStartOver != null) {
            TextButton(
                onClick = onStartOver,
                enabled = !isLoading,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp)
            ) {
                Text("Start Over")
            }
        }
    }
}

@Composable
fun PayScreen(
    selectedArrangement: FloristArrangement?,
    sharedUnderstanding: SharedUnderstanding,
    onCheckout: (String) -> Unit,
    checkoutTotal: Double? = null,
    onBack: (() -> Unit)? = null,
    onStartOver: (() -> Unit)? = null,
    isLoading: Boolean = false,
    modifier: Modifier = Modifier
) {
    var cardMessage by remember { mutableStateOf("Happy Birthday Mom! Love always.") }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        AsoDisclaimer()

        Text(
            text = "Order & Delivery Summary",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Order Details Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = selectedArrangement?.name ?: "No Arrangement Selected",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(text = "Delivery: ${sharedUnderstanding.deliveryDate ?: "Today (Same-Day)"}", style = MaterialTheme.typography.bodyMedium)
                Text(text = "Destination: Ref# LILY-PARIS-01 (Zero-PII, ADR-013)", style = MaterialTheme.typography.bodyMedium)
                Spacer(modifier = Modifier.height(8.dp))
                Divider()
                Spacer(modifier = Modifier.height(8.dp))
                val productPrice = selectedArrangement?.price ?: 0.0
                val total = checkoutTotal ?: productPrice
                if (checkoutTotal != null && checkoutTotal > productPrice) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(text = "Arrangement:", style = MaterialTheme.typography.bodyMedium)
                        Text(text = "$${"%.2f".format(productPrice)}", style = MaterialTheme.typography.bodyMedium)
                    }
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(text = "Delivery:", style = MaterialTheme.typography.bodyMedium)
                        Text(
                            text = "$${"%.2f".format(checkoutTotal - productPrice)}",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(text = "Total:", style = MaterialTheme.typography.titleMedium)
                    Text(
                        text = "$${"%.2f".format(total)}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Card Message input
        OutlinedTextField(
            value = cardMessage,
            onValueChange = { cardMessage = it },
            label = { Text("Enclosure Card Message") },
            modifier = Modifier.fillMaxWidth(),
            maxLines = 3
        )

        Spacer(modifier = Modifier.weight(1f))

        // Single Primary Confirm CTA (NFR-017 zero-PII checkout)
        Button(
            onClick = { onCheckout(cardMessage) },
            enabled = selectedArrangement != null && !isLoading,
            modifier = Modifier
                .fillMaxWidth()
                .height(54.dp)
        ) {
            Text(if (isLoading) "Placing order…" else "Confirm & Place Order ✓")
        }

        if (onBack != null) {
            OutlinedButton(
                onClick = onBack,
                enabled = !isLoading,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp)
            ) {
                Text("← Back to Pick")
            }
        }
        if (onStartOver != null) {
            TextButton(
                onClick = onStartOver,
                enabled = !isLoading,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Start Over")
            }
        }
    }
}

@Composable
fun TrackingScreen(
    orderResult: OrderResult?,
    onStartOver: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "💐 Order Confirmed!",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(16.dp))

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Text(text = "Order Number: ${orderResult?.orderId}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))
                Text(text = "Status: ${orderResult?.status} (Preparing in atelier)", style = MaterialTheme.typography.bodyMedium)
                Text(text = "Delivery ETA: ${orderResult?.estimatedDelivery}", style = MaterialTheme.typography.bodyMedium)
                Text(text = "Total Charged: $${"%.2f".format(orderResult?.totalAmount ?: 0.0)}", style = MaterialTheme.typography.bodyMedium)
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = onStartOver,
            modifier = Modifier
                .fillMaxWidth()
                .height(50.dp)
        ) {
            Text("Start New Arrangement")
        }
    }
}
