package link.artof.aea.companion

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import link.artof.aea.companion.data.repository.JourneyStage
import link.artof.aea.companion.data.repository.SessionRepository
import link.artof.aea.companion.data.wallet.EdgeWallet
import link.artof.aea.companion.data.wallet.EncryptedPrefsWalletStore
import link.artof.aea.companion.ui.components.StageProgressBar
import link.artof.aea.companion.ui.screens.ContactFloristDialog
import link.artof.aea.companion.ui.screens.NeedScreen
import link.artof.aea.companion.ui.screens.PayScreen
import link.artof.aea.companion.ui.screens.PickScreen
import link.artof.aea.companion.ui.screens.TrackingScreen
import link.artof.aea.companion.ui.theme.LilyCompanionTheme

class MainActivity : ComponentActivity() {
    // ADR-020 Layer 2: back the device-owned Edge Wallet with Keystore-encrypted
    // storage. Built lazily so applicationContext is available (first use is in
    // onCreate). Falls back to the in-memory default only if secure storage is
    // unavailable on the device.
    private val repository: SessionRepository by lazy {
        val wallet = try {
            EdgeWallet(EncryptedPrefsWalletStore(applicationContext))
        } catch (_: Exception) {
            null
        }
        if (wallet != null) SessionRepository(wallet = wallet) else SessionRepository()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            LilyCompanionTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    LilyCompanionApp(repository)
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LilyCompanionApp(repository: SessionRepository) {
    val stage by repository.currentStage.collectAsState()
    val messages by repository.messages.collectAsState()
    val arrangements by repository.arrangements.collectAsState()
    val selectedArrangement by repository.selectedArrangement.collectAsState()
    val sharedUnderstanding by repository.sharedUnderstanding.collectAsState()
    val budgetPromptResolved by repository.budgetPromptResolved.collectAsState()
    val orderResult by repository.orderResult.collectAsState()
    val isLoading by repository.isLoading.collectAsState()
    val errorMessage by repository.errorMessage.collectAsState()
    val orderSummaryTotal by repository.orderSummaryTotal.collectAsState()
    val deliveryWindow by repository.deliveryWindow.collectAsState()
    val destinationReference by repository.destinationReference.collectAsState()
    val deliveryDate by repository.deliveryDate.collectAsState()
    val escalationAck by repository.escalationAck.collectAsState()
    var showContactFlorist by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    LaunchedEffect(Unit) {
        repository.ensureSession()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "Lily's Florist Companion",
                        style = MaterialTheme.typography.headlineMedium
                    )
                },
                actions = {
                    TextButton(onClick = { showContactFlorist = true }) {
                        Text("Contact Florist")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.background,
                    titleContentColor = MaterialTheme.colorScheme.onBackground
                )
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            if (stage != JourneyStage.TRACKING) {
                StageProgressBar(currentStage = stage)
            }

            if (isLoading) {
                LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
            }

            errorMessage?.let { err ->
                Surface(
                    color = MaterialTheme.colorScheme.errorContainer,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(
                            text = err,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            style = MaterialTheme.typography.bodyMedium
                        )
                        TextButton(onClick = { repository.clearError() }) {
                            Text("Dismiss")
                        }
                    }
                }
            }

            when (stage) {
                JourneyStage.NEED -> {
                    NeedScreen(
                        messages = messages,
                        sharedUnderstanding = sharedUnderstanding,
                        isLoading = isLoading,
                        budgetPromptResolved = budgetPromptResolved,
                        onSendMessage = { text ->
                            scope.launch { repository.postUserMessage(text) }
                        },
                        onBudgetChoice = { label, ceiling ->
                            scope.launch { repository.setBudgetChoice(label, ceiling) }
                        },
                        onOccasionChoice = { label ->
                            scope.launch { repository.setOccasionChoice(label) }
                        },
                        onSkipBudget = { repository.skipBudget() },
                        onContinueToPick = { draft ->
                            scope.launch { repository.continueToPick(draft) }
                        },
                        onStartOver = { scope.launch { repository.startOver() } }
                    )
                }
                JourneyStage.PICK -> {
                    PickScreen(
                        arrangements = arrangements,
                        selectedArrangement = selectedArrangement,
                        isLoading = isLoading,
                        budgetLabel = sharedUnderstanding.budget,
                        onSelectArrangement = { arrangement ->
                            scope.launch { repository.selectArrangement(arrangement) }
                        },
                        onContinueToPay = { repository.moveToPayStage() },
                        onBack = { repository.backToNeed() },
                        onStartOver = { scope.launch { repository.startOver() } }
                    )
                }
                JourneyStage.PAY -> {
                    PayScreen(
                        selectedArrangement = selectedArrangement,
                        sharedUnderstanding = sharedUnderstanding,
                        isLoading = isLoading,
                        checkoutTotal = orderSummaryTotal
                            ?: repository.displayCheckoutTotal(selectedArrangement?.price),
                        deliveryDate = deliveryDate,
                        deliveryWindow = deliveryWindow,
                        destinationReference = destinationReference,
                        onDeliveryDateOffset = { repository.setDeliveryDateOffset(it) },
                        onDeliveryWindow = { repository.setDeliveryWindow(it) },
                        onDestinationReference = { repository.setDestinationReference(it) },
                        onContactFlorist = { showContactFlorist = true },
                        onCheckout = { cardMsg ->
                            scope.launch { repository.completeCheckout(cardMsg) }
                        },
                        onBack = { repository.backToPick() },
                        onStartOver = { scope.launch { repository.startOver() } }
                    )
                }
                JourneyStage.TRACKING -> {
                    TrackingScreen(
                        orderResult = orderResult,
                        escalationAck = escalationAck,
                        onContactFlorist = { showContactFlorist = true },
                        onStartOver = {
                            scope.launch { repository.startOver() }
                        }
                    )
                }
            }
        }
    }

    if (showContactFlorist) {
        ContactFloristDialog(
            onDismiss = { showContactFlorist = false },
            onSubmit = { reason ->
                scope.launch { repository.requestEscalation(reason) }
            },
            acknowledgement = escalationAck,
            isLoading = isLoading
        )
    }
}
