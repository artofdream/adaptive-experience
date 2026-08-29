# Milestone M19: Native Mobile Companion Phase 0 Android Scaffold & CI Pipeline

> **Tags**: #aea #second-brain #native-mobile #android #compose #ci-cd #firebase #knowledge-first
> **Captured**: 2026-08-29
> **Author**: @aea-senior-software-engineer, @aea-devsecops-platform, @aea-ux-designer, @aea-mr-coordinator
> **GitLab**: Closes #307 (Firebase Crashlytics / App Distribution stay on #308)
> **Owners to inherit**: @aea-senior-software-engineer, @aea-devsecops-platform, @aea-mr-coordinator

---

## 1. Context & Objectives

Following the chartering of Milestone **M19 (Native Mobile Companion — Android)** in `roadmap.md` and the acceptance of `ADR-017`, `ADR-018`, `ADR-019`, and `native-mobile-ux-specification.md`, this delivery implements:
1. **Phase 0 Android App Scaffold (`clients/mobile/android/`)**:
   - Modern Kotlin + Jetpack Compose application targeting Android 15 (API 35) and Java 21.
   - Implements the 3-stage linear concierge (**Need $\to$ Pick $\to$ Pay $\to$ Tracking**) for Journey 1 (Same-Day Delivery happy path).
   - Enforces single-CTA per screen, fail-closed inventory badges (`NFR-009`), zero-PII checkout (`NFR-017`), destination reference (`ADR-013`), and ASO automated concierge disclaimers (`FR-009`).
   - Clean type-safe HTTP client consuming existing Gateway/BFF endpoints (`/api/v1/session`, `/api/v1/conversation/messages`, `/api/v1/selection`, `/api/v1/checkout`).
2. **24/7 Cloud GitLab CI Pipeline (`.gitlab-ci.yml`)**:
   - Required `android-build-debug` on `cimg/android:2024.04` (OpenJDK 21, matching the app `jvmTarget`). `2024.01` is JDK 17 and cannot load those unit tests.
   - Runs `assembleDebug` and `testDebugUnitTest` in the same required job. Do not `allow_failure` this job.

---

## 2. Verification

* `CompanionUnitTests.kt`: Verifies initial state, Journey 1 message parsing, fail-closed sold-out handling, linear stage transitions, and JSON serialization.
* `14/14` Pre-flight quality guards passing cleanly.

Existing IDs: [[2026-08-29-native-mobile-companion-system-docs-and-toolkit]], [[2026-08-29-harness-memory-engineering-evaluation-synthesis]], [[2026-08-29-parallel-runner-claim-rule]], [[2026-08-29-finops-cost-optimization-rationale-and-enforcement]].
