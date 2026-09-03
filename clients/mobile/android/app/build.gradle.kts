plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.google.services)
    alias(libs.plugins.firebase.crashlytics)
    alias(libs.plugins.firebase.appdistribution)
    alias(libs.plugins.paparazzi)
}

// Play upload signing (#347). Env only — never a committed keystore.
// Debug builds stay debug-signed as today when these are unset.
val uploadKeystorePath = System.getenv("ANDROID_UPLOAD_KEYSTORE")
val uploadKeystorePassword = System.getenv("ANDROID_UPLOAD_KEYSTORE_PASSWORD")
val uploadKeyAlias = System.getenv("ANDROID_UPLOAD_KEY_ALIAS")
val uploadKeyPassword = System.getenv("ANDROID_UPLOAD_KEY_PASSWORD")
val releaseSigningReady =
    !uploadKeystorePath.isNullOrBlank() &&
        !uploadKeystorePassword.isNullOrBlank() &&
        !uploadKeyAlias.isNullOrBlank() &&
        !uploadKeyPassword.isNullOrBlank() &&
        file(uploadKeystorePath).isFile

android {
    namespace = "link.artof.aea.companion"
    compileSdk = 36

    defaultConfig {
        applicationId = "link.artof.aea.companion"
        minSdk = 26
        targetSdk = 36
        // versionName must change with versionCode so Play Internal / dumpsys are easy to track.
        // Scheme: 0.1.0-alpha.<versionCode>
        versionCode = 5
        versionName = "0.1.0-alpha.5"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    signingConfigs {
        if (releaseSigningReady) {
            create("release") {
                storeFile = file(requireNotNull(uploadKeystorePath))
                storePassword = requireNotNull(uploadKeystorePassword)
                keyAlias = requireNotNull(uploadKeyAlias)
                keyPassword = requireNotNull(uploadKeyPassword)
            }
        }
    }

    buildTypes {
        release {
            // #390 honesty: release must never be debuggable (Play AABs / ASUS gate).
            // Android default is false; set explicitly so FAD/debug overwrite is obvious in review.
            isDebuggable = false
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            if (releaseSigningReady) {
                signingConfig = signingConfigs.getByName("release")
            }
        }
        debug {
            // Same applicationId as release so CI google-services.json
            // (Firebase client link.artof.aea.companion) matches assembleDebug.
            // Do not add a .debug suffix — that package is not in the #308 client.
            isDebuggable = true
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_21
        targetCompatibility = JavaVersion.VERSION_21
    }
    kotlinOptions {
        jvmTarget = "21"
    }
    buildFeatures {
        compose = true
        // Unit test debugApplicationIdMatchesFirebaseClient reads BuildConfig.APPLICATION_ID.
        buildConfig = true
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}


// Firebase App Distribution (#363 Phase B). Credentials from CI env only.
// Never commit a service-account JSON. Job is manual / omitted when unset.
val fadCredentials = System.getenv("FIREBASE_APP_DISTRIBUTION_CREDENTIALS")
val fadGroups = System.getenv("FIREBASE_APP_DISTRIBUTION_GROUPS") ?: "ux-testers"
val fadReleaseNotes =
    System.getenv("FIREBASE_APP_DISTRIBUTION_RELEASE_NOTES")
        ?: "Companion UX validation build (debug). Not Play-signed. Local mock until BFF (#360/#362)."

firebaseAppDistribution {
    // Plugin reads app id from google-services.json when present.
    artifactType = "APK"
    groups = fadGroups
    releaseNotes = fadReleaseNotes
    if (!fadCredentials.isNullOrBlank()) {
        serviceCredentialsFile = fadCredentials
    }
}

tasks.matching { it.name == "bundleRelease" }.configureEach {
    doFirst {
        check(releaseSigningReady) {
            "bundleRelease requires env ANDROID_UPLOAD_KEYSTORE (keystore file path), " +
                "ANDROID_UPLOAD_KEYSTORE_PASSWORD, ANDROID_UPLOAD_KEY_ALIAS, and " +
                "ANDROID_UPLOAD_KEY_PASSWORD. Do not commit a keystore."
        }
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation(libs.androidx.material.icons.extended)
    implementation(libs.androidx.navigation.compose)

    // ADR-020 Layer 2 Edge Wallet: at-rest encryption via Android Keystore.
    implementation(libs.androidx.security.crypto)

    implementation(libs.kotlinx.coroutines.core)
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.kotlinx.serialization.json)

    implementation(libs.ktor.client.core)
    implementation(libs.ktor.client.cio)
    implementation(libs.ktor.client.content.negotiation)
    implementation(libs.ktor.serialization.kotlinx.json)

    implementation(platform(libs.firebase.bom))
    implementation(libs.firebase.crashlytics)
    implementation(libs.firebase.analytics)
    // No firebase-messaging / FCM — ADR-019 is a decision record only.

    testImplementation(libs.junit)
    testImplementation(libs.ktor.client.mock)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
}


// #364: Paparazzi snapshots run only via recordPaparazziDebug /
// verifyPaparazziDebug (CI job android-compose-screenshots). Exclude from
// default testDebugUnitTest so android-build-debug stays green without
// committed goldens on first land.
tasks.withType<Test>().configureEach {
    val runningPaparazzi = gradle.startParameter.taskNames.any {
        it.contains("Paparazzi", ignoreCase = true)
    }
    if (!runningPaparazzi) {
        filter {
            excludeTestsMatching("*Paparazzi*")
        }
    }
}
