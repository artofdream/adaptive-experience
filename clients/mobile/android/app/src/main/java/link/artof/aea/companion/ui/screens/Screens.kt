package link.artof.aea.companion.ui.screens

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import coil.compose.AsyncImage
import link.artof.aea.companion.data.model.Arrangement as FloristArrangement
import link.artof.aea.companion.data.model.ChatMessage
import link.artof.aea.companion.data.model.OrderResult
import link.artof.aea.companion.data.model.SharedUnderstanding
import link.artof.aea.companion.data.repository.SessionRepository
import link.artof.aea.companion.ui.components.*

@Composable
fun NeedScreen(
    messages: List<ChatMessage>,
    sharedUnderstanding: SharedUnderstanding,
    onSendMessage: (String) -> Unit,
    onContinueToPick: (draftText: String) -> Unit,
    onBudgetChoice: (label: String, ceiling: Double?) -> Unit = { _, _ -> },
    onOccasionChoice: (label: String) -> Unit = {},
    onSkipBudget: () -> Unit = {},
    budgetPromptResolved: Boolean = false,
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

        // Quick Suggestion Chips (only shown on fresh start before occasion or user message)
        val hasUserMessages = messages.any { it.sender == "user" }
        val hasOccasion = !sharedUnderstanding.occasion.isNullOrEmpty()
        if (!hasUserMessages && !hasOccasion) {
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
        }

        // Text input row
        val sendDraft: () -> Unit = {
            if (inputText.isNotBlank()) {
                onSendMessage(inputText)
                inputText = ""
            }
        }
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = inputText,
                onValueChange = { inputText = it },
                placeholder = { Text("Tell Lily what you need...") },
                modifier = Modifier.weight(1f),
                maxLines = 2,
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                keyboardActions = KeyboardActions(onSend = { sendDraft() }),
            )
            Spacer(modifier = Modifier.width(8.dp))
            Button(
                onClick = sendDraft,
                enabled = !isLoading && inputText.isNotBlank(),
                modifier = Modifier.height(56.dp)
            ) {
                Text("Send")
            }
        }

        // Occasion correction when free-text missed OCCASIONS keywords (#400).
        if (hasUserMessages && !hasOccasion) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 4.dp)
            ) {
                Text(
                    text = "What is the occasion? (optional — you can continue without one)",
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Spacer(modifier = Modifier.height(4.dp))
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    SessionRepository.OCCASION_CORRECTION_TOKENS.forEach { token ->
                        FilterChip(
                            selected = false,
                            onClick = { onOccasionChoice(token) },
                            enabled = !isLoading,
                            label = { Text(token.replaceFirstChar { it.uppercase() }) }
                        )
                    }
                }
            }
        }

        // Budget ask after occasion unlock *or* a persisted Need message (#359 / #374 / #400)
        val showBudget = hasOccasion || hasUserMessages
        if (showBudget) {
            val currentBudget = sharedUnderstanding.budget
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 4.dp)
            ) {
                Text(
                    text = "Budget for this arrangement:",
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Spacer(modifier = Modifier.height(4.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    FilterChip(
                        selected = currentBudget == "Under $50",
                        onClick = { onBudgetChoice("Under $50", 50.0) },
                        enabled = !isLoading,
                        label = { Text("<$50") }
                    )
                    FilterChip(
                        selected = currentBudget == "$50–100",
                        onClick = { onBudgetChoice("$50–100", 100.0) },
                        enabled = !isLoading,
                        label = { Text("$50–100") }
                    )
                    FilterChip(
                        selected = currentBudget == "$100+",
                        onClick = { onBudgetChoice("$100+", null) },
                        enabled = !isLoading,
                        label = { Text("$100+") }
                    )
                    FilterChip(
                        selected = currentBudget == "skipped",
                        onClick = onSkipBudget,
                        enabled = !isLoading,
                        label = { Text("No limit") }
                    )
                }
            }
        }

        // Primary Single CTA (UX Rule: exactly one primary CTA per stage)
        // #400: non-empty free-text (draft or posted) unlocks Continue like web Need.
        val canContinue = SessionRepository.canContinueFromNeed(
            occasion = sharedUnderstanding.occasion,
            budgetPromptResolved = budgetPromptResolved,
            hasPersistedNeedText = hasUserMessages,
            draftNeedText = inputText,
            hasUsableIntentFacet = SessionRepository.hasUsableIntentFacet(sharedUnderstanding),
        )
        Button(
            onClick = { onContinueToPick(inputText) },
            enabled = canContinue && !isLoading,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 4.dp)
                .height(52.dp)
        ) {
            Text(
                when {
                    !canContinue && hasOccasion && !budgetPromptResolved ->
                        "Choose a Budget Range to Continue"
                    !canContinue -> "Tell Lily what you need to continue"
                    !sharedUnderstanding.occasion.isNullOrBlank() ->
                        "View Arrangements (${sharedUnderstanding.occasion}) →"
                    else -> "View Arrangements →"
                }
            )
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
    quantity: Int = 1,
    onQuantityChange: (Int) -> Unit = {},
    budgetLabel: String? = null,
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

        if (!budgetLabel.isNullOrBlank()) {
            Text(
                text = if (budgetLabel == "skipped")
                    "Budget not set (skipped on Need)."
                else
                    "Filtering / ranking with budget: $budgetLabel (local price filter when catalog has prices).",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 2.dp)
            )
        }

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

        if (selectedArrangement != null) {
            QuantityStepper(
                quantity = quantity,
                onQuantityChange = onQuantityChange,
                enabled = !isLoading,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
            )
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
                if (selectedArrangement != null) {
                    val line = selectedArrangement.price * quantity
                    val qtyLabel = if (quantity > 1) " × $quantity" else ""
                    "Continue to Checkout ($${"%.2f".format(line)}$qtyLabel) →"
                } else {
                    "Select an Arrangement to Continue"
                }
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
    quantity: Int = 1,
    onQuantityChange: (Int) -> Unit = {},
    checkoutTotal: Double? = null,
    deliveryDate: String = "",
    deliveryWindow: String = "afternoon",
    destinationReference: String = "home",
    onDeliveryDateOffset: (Int) -> Unit = {},
    onDeliveryWindow: (String) -> Unit = {},
    onDestinationReference: (String) -> Unit = {},
    onContactFlorist: (() -> Unit)? = null,
    onBack: (() -> Unit)? = null,
    onStartOver: (() -> Unit)? = null,
    isLoading: Boolean = false,
    modifier: Modifier = Modifier
) {
    // #389: occasion-aware enclosure default — never Birthday Mom on Anniversary.
    var cardMessage by remember(
        sharedUnderstanding.occasion,
        sharedUnderstanding.recipient
    ) {
        mutableStateOf(
            link.artof.aea.companion.data.repository.SessionRepository.defaultCardMessage(
                occasion = sharedUnderstanding.occasion,
                recipient = sharedUnderstanding.recipient
            )
        )
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
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
                val payImage = selectedArrangement?.imageUrl.orEmpty()
                if (payImage.isNotBlank()) {
                    AsyncImage(
                        model = payImage,
                        contentDescription = selectedArrangement?.name,
                        contentScale = ContentScale.Crop,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(120.dp)
                            .clip(RoundedCornerShape(10.dp))
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                }
                Text(
                    text = selectedArrangement?.name ?: "No Arrangement Selected",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "When: ${deliveryDate.ifBlank { sharedUnderstanding.deliveryDate ?: "today" }} · $deliveryWindow",
                    style = MaterialTheme.typography.bodyMedium
                )
                Text(
                    text = "Destination: $destinationReference (opaque ref, ADR-013 — not a street)",
                    style = MaterialTheme.typography.bodyMedium
                )
                val budgetHonesty = sharedUnderstanding.budget
                if (!budgetHonesty.isNullOrBlank()) {
                    val ceiling = link.artof.aea.companion.data.repository.SessionRepository
                        .parseBudgetCeiling(budgetHonesty)
                    val selectedPrice = selectedArrangement?.price
                    val honesty = when {
                        budgetHonesty == "skipped" -> "Budget: skipped on Need"
                        ceiling != null && selectedPrice != null && selectedPrice > ceiling ->
                            "Budget: $budgetHonesty — selected price exceeds ceiling"
                        else -> "Budget: $budgetHonesty"
                    }
                    Text(text = honesty, style = MaterialTheme.typography.bodyMedium)
                }
                Spacer(modifier = Modifier.height(8.dp))
                QuantityStepper(
                    quantity = quantity,
                    onQuantityChange = onQuantityChange,
                    enabled = !isLoading && selectedArrangement != null
                )
                Spacer(modifier = Modifier.height(8.dp))
                Divider()
                Spacer(modifier = Modifier.height(8.dp))
                val unitPrice = selectedArrangement?.price ?: 0.0
                val productPrice = unitPrice * quantity
                val total = checkoutTotal ?: productPrice
                if (checkoutTotal != null && checkoutTotal > productPrice) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        val arrangementLabel = if (quantity > 1)
                            "Arrangement (${quantity}x):"
                        else
                            "Arrangement:"
                        Text(text = arrangementLabel, style = MaterialTheme.typography.bodyMedium)
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

        Text(
            text = "Delivery date",
            style = MaterialTheme.typography.titleSmall
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            val todayIso = java.time.LocalDate.now().toString()
            val tomorrowIso = java.time.LocalDate.now().plusDays(1).toString()
            FilterChip(
                selected = deliveryDate == todayIso || deliveryDate.isBlank(),
                onClick = { onDeliveryDateOffset(0) },
                enabled = !isLoading,
                label = { Text("Today") }
            )
            FilterChip(
                selected = deliveryDate == tomorrowIso,
                onClick = { onDeliveryDateOffset(1) },
                enabled = !isLoading,
                label = { Text("Tomorrow") }
            )
        }

        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Window",
            style = MaterialTheme.typography.titleSmall
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            listOf("morning", "afternoon", "evening").forEach { window ->
                FilterChip(
                    selected = deliveryWindow == window,
                    onClick = { onDeliveryWindow(window) },
                    enabled = !isLoading,
                    label = { Text(window.replaceFirstChar { it.uppercase() }) }
                )
            }
        }

        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Destination reference",
            style = MaterialTheme.typography.titleSmall
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            listOf("home", "work").forEach { ref ->
                FilterChip(
                    selected = destinationReference == ref,
                    onClick = { onDestinationReference(ref) },
                    enabled = !isLoading,
                    label = { Text(ref.replaceFirstChar { it.uppercase() }) }
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Card Message input
        OutlinedTextField(
            value = cardMessage,
            onValueChange = { cardMessage = it },
            label = { Text("Enclosure Card Message") },
            supportingText = { Text("Complimentary handwritten card included with delivery") },
            modifier = Modifier.fillMaxWidth(),
            maxLines = 3
        )

        Spacer(modifier = Modifier.height(16.dp))

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
        if (onContactFlorist != null) {
            TextButton(
                onClick = onContactFlorist,
                enabled = !isLoading,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Contact Florist")
            }
        }
    }
}

@Composable
fun TrackingScreen(
    orderResult: OrderResult?,
    onStartOver: () -> Unit,
    onContactFlorist: (() -> Unit)? = null,
    escalationAck: String? = null,
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

        if (!escalationAck.isNullOrBlank()) {
            Text(
                text = escalationAck,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(12.dp))
        }

        if (onContactFlorist != null) {
            OutlinedButton(
                onClick = onContactFlorist,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
            ) {
                Text("Contact Florist")
            }
            Spacer(modifier = Modifier.height(8.dp))
        }

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

@Composable
fun ContactFloristDialog(
    onDismiss: () -> Unit,
    onSubmit: (String) -> Unit,
    acknowledgement: String?,
    isLoading: Boolean
) {
    val reasons = listOf(
        "unresolved_request" to "Unresolved request",
        "order_issue" to "Order issue",
        "delivery_issue" to "Delivery issue",
        "product_question" to "Product question"
    )
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Contact Florist") },
        text = {
            Column {
                Text(
                    text = "A person on the florist team will see this session. Choose a reason — no street address or card details.",
                    style = MaterialTheme.typography.bodyMedium
                )
                Spacer(modifier = Modifier.height(12.dp))
                reasons.forEach { (value, label) ->
                    TextButton(
                        onClick = { onSubmit(value) },
                        enabled = !isLoading,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(label)
                    }
                }
                if (!acknowledgement.isNullOrBlank()) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = acknowledgement,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) { Text("Close") }
        }
    )
}
