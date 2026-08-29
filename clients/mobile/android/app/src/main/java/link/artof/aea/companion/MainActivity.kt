package link.artof.aea.companion

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import link.artof.aea.companion.data.repository.JourneyStage
import link.artof.aea.companion.data.repository.SessionRepository
import link.artof.aea.companion.ui.components.StageProgressBar
import link.artof.aea.companion.ui.screens.*
import link.artof.aea.companion.ui.theme.LilyCompanionTheme

class MainActivity : ComponentActivity() {
    private val repository = SessionRepository()

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
    val orderResult by repository.orderResult.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "Lily\'s Florist Companion",
                        style = MaterialTheme.typography.headlineMedium
                    )
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

            when (stage) {
                JourneyStage.NEED -> {
                    NeedScreen(
                        messages = messages,
                        sharedUnderstanding = sharedUnderstanding,
                        onSendMessage = { repository.postUserMessage(it) },
                        onContinueToPick = { repository.moveToPickStage() }
                    )
                }
                JourneyStage.PICK -> {
                    PickScreen(
                        arrangements = arrangements,
                        selectedArrangement = selectedArrangement,
                        onSelectArrangement = { repository.selectArrangement(it) },
                        onContinueToPay = { repository.moveToPayStage() }
                    )
                }
                JourneyStage.PAY -> {
                    PayScreen(
                        selectedArrangement = selectedArrangement,
                        sharedUnderstanding = sharedUnderstanding,
                        onCheckout = { cardMsg -> repository.completeCheckout(cardMsg) }
                    )
                }
                JourneyStage.TRACKING -> {
                    TrackingScreen(
                        orderResult = orderResult,
                        onStartOver = { repository.startOver() }
                    )
                }
            }
        }
    }
}
