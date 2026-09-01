# Promotion candidate — Native mobile companion: system documentation & toolset needed

> **Tags**: #aea #promote #second-brain #native-mobile
> **Captured**: 2026-08-29
> **Status**: sponsor-directed — proceeding, Android first, gradual (updated 2026-08-29, same day)
> **Source**: Figma exploration prototype built this session — [Lily's Florist — Native Mobile (J1–J4)](https://www.figma.com/design/BcoNF0vHDV8Pb3efDT5eBf), 9 mobile screens + cover walking journeys J1–J4 through the target Need→Pick→Pay flow, with a wired click-through prototype.

Inherits [[2026-08-27-path-b-dual-viewport-ux-loop-j1-j4]] (J1–J4 clip
evidence this note's screens were translated from). Journeys
[[J1]] [[J2]] [[J3]] [[J4]]. Sibling: [[2026-08-27-session-memory-log-cf054-path-b-ux-in-coherence-loop]].
Operator File-var lesson (Play upload keystore, not Firebase):
[[2026-09-01-android-upload-keystore-gitlab-file-var]].

## 2026-08-29 sponsor decision log

Sponsor (human) direction, same day as capture: native mobile pathway **is
to happen** — not deferred further. Constraints given directly:

- **Gradual implementation.** Not a big-bang native release.
- **Android first.** iOS sequenced after Android's first phase is validated.
- **Known blocker named up front**: Google Play Developer account **validated 2026-08-31** (sponsor). Remaining Slice D work is first `.aab` / Play App Signing SHA-1 in Firebase / install-from-closed-track — Unknown until a bundle exists ([#346](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/346), [#347](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/347)).

This is a sponsor steer, not yet a `@aea-product-owner` formal go/no-go
against a named milestone (no milestone exists for this — see §Vision below).
Per the [product-owner role split](../../.cursor/skills/aea-product-owner/SKILL.md),
the sponsor may set direction; PO still owns turning it into an accepted
slice with evidence, and PM still owns turning that into bench assignments.
Both are done below in the same pass since the sponsor's direction is
unambiguous and doesn't contradict published vision — it activates the
Future-extension bullet already in product-vision.md rather than inventing
new product scope.

## 2026-08-29 pre-work plan (Play-account-independent), PO/PM sign-off

**Honesty flag, upfront:** everything in this section is **proposed, not
started**, except the two rows marked Done. Nothing below has a GitLab
issue, branch, or MR yet. No code exists. `docs/07-roadmap/roadmap.md` has
**not** been edited — the M19 row proposed here is a recommendation, not a
committed change. Treat every "Owner" below as a *proposed* assignment
pending the actual `@aea-project-manager` bench-assignment turn (opening
the issue and invoking the owner in the same turn, per this repo's SOP) —
not as work that has begun.

**Goal:** everything that does *not* need the Google Play Developer account
gets done while it activates, so Phase 1 (closed testing) has zero
engineering lead time the moment the account clears.

| # | Item | Needs Play account? | Status | Proposed owner |
|---|------|:---:|---|---|
| — | Figma native-screen prototype (J1–J4, 10 frames, wired click-through) | No | **Done** — [file](https://www.figma.com/design/BcoNF0vHDV8Pb3efDT5eBf) | (this session) |
| — | This research note (candidate architecture + toolkit doc) | No | **Done** — draft, not promoted to `docs/` | (this session) |
| 1 | ADR: native client architecture (one BFF, two generated clients) | No | Not started | `@aea-senior-software-engineer` |
| 2 | ADR: mobile session & auth model (Keystore/Keychain, no login) | No | Not started | `@aea-senior-software-engineer` |
| 3 | ADR: native push & proactive engagement — **decision record only**, no push code until FR-016's own milestone | No | Not started | `@aea-senior-software-engineer` |
| 4 | Native Mobile UX Specification — formalize the Figma prototype into a doc parallel to `path-b-dual-viewport-specification.md` | No | Not started | `@aea-ux-designer` |
| 5 | Phase 0 Android scaffold: Compose + client generated from the existing BFF OpenAPI contract (ADR-008) + J1 happy path only, sideload-only build | No | Not started — depends on #1, #2 landing first | `@aea-senior-software-engineer` |
| 6 | CI: Android build pipeline + crash reporting (e.g. Firebase Crashlytics) + Firebase App Distribution for internal testers | **No** — Firebase App Distribution and Crashlytics are separate from Play Console | Not started | `@aea-devsecops-platform` |
| 7 | Native journey-walker port (J1–J4, Compose UI test), parallel to the existing Playwright web walker | No | Not started — depends on #5 existing first | `@aea-senior-software-engineer` / `@aea-customer-journey` |
| — | Play Console: closed testing track, store listing, signing upload, public rollout | **Yes** | Play Developer account validated and Android app created 2026-08-31 (sponsor confirmation; package `link.artof.aea.companion`; display name Lily's Florist Companion; closed testers email list exists). Store listing / public rollout still out of this slice. First `.aab`, Play App Signing SHA-1 in Firebase, and install-from-track are **Unknown** (CI on `main` is `assembleDebug` APK only). Probe: [#346](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/346). Follow-on bundle: [#347](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/347). | `@aea-devsecops-platform` |

**Dependency order** (docs before code, always): `1, 2, 3, 4` (docs-only, no
Docker integration, can run in parallel) → `5, 6` (5 needs 1+2 merged; 6 has
no dependency, can start immediately) → `7` (needs 5).

**Timeline — sequence, not calendar.** This repo's PM protocol explicitly
does not use story-point velocity or committed dates, so this is ordering +
rough relative sizing, not a date commitment:

- **Slice A (docs, parallel, smallest)**: items 1–4. Docs-only MRs, no
  Docker integration gate. Fastest path to unblocking Slice B.
- **Slice B (build, parallel where possible)**: item 6 can start the moment
  Slice A starts (no dependency). Item 5 waits on ADRs 1+2.
- **Slice C (validate)**: item 7, after item 5 has a running scaffold.
- **Slice D (Play Console, in progress)**: account + app + closed testers list exist 2026-08-31 ([#346](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/346)). Do not claim testers can install, and do not claim SHA-1 is in Firebase, until a first `.aab` is uploaded ([#347](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/347)).

### Sign-off

**`@aea-product-owner` — Accept.** Names milestone
`M19 — Native Mobile Companion, Android (Reference Extension)`, scoped to
J1–J4 parity on Android only, no new FR/NFR IDs (existing coverage, new
client surface). **Not yet written into `docs/07-roadmap/roadmap.md`** —
recommended, pending explicit confirmation to edit a canonical file.

**`@aea-project-manager` — Approves the Slice A–C assignment plan above**
as the bench plan once M19 is named. Blocker (Play account) logged as a
single `user` wait tag against **Slice D only** — it does not block or
excuse Slices A–C. **No GitLab issue has been opened yet** — per this
repo's SOP, opening the issue and invoking the owner happen in the same
turn as the actual assignment, which has not happened yet; this document is
the proposal that assignment would be based on.

## Cost estimate (`@aea-cost-guardian`)

**Honesty flag:** nothing below is a measured AWS Cost Explorer figure —
there is no deployed native traffic to measure. These are **planning
estimates** from typical vendor pricing and this repo's existing AWS
posture, marked accordingly. Anything not knowable without a usage forecast
is marked **Unknown**, not guessed.

**One-time / account costs:**

| Item | Est. cost | Status |
|---|---|---|
| Google Play Developer account | $25 one-time | Already in motion — the named blocker, sponsor-paid |
| Apple Developer Program (iOS phase, later) | $99/year | Not needed yet — Android first per sponsor direction |
| Code signing (Play App Signing / Apple) | Included in the above | — |

**Recurring, tooling:**

| Item | Est. cost | Status |
|---|---|---|
| Firebase (Crashlytics + App Distribution) | $0 — Spark (free) tier covers Phase 0/1 internal-tester volumes | Re-check if Blaze (pay-as-you-go) is needed once volume grows — Unknown until real usage exists |
| Firebase Cloud Messaging (push, Phase 2+) | $0 — FCM has no send cost | Not in scope until the push ADR + FR-016 milestone |
| GitLab CI minutes for Android build/test jobs | Planning estimate: +5–15 min per pipeline run added to existing shared CI minutes budget | Depends on this repo's current CI minute allowance — **Unknown**, not checked this session |

**Cloud impact (existing AWS Path B, `aea-pilot`) — no new cost *driver*, only load to re-baseline:**

- **No new AWS line item.** The native client is a new *caller* of the
  existing Gateway/BFF (ADR-007) — it does not add a new ECS service, RDS
  instance, or MSK cluster. Same modular-monolith backend serves both
  clients.
- **Re-baseline, don't budget yet:** Fargate autoscaling (`min=2, max=20`,
  this skill's own existing governance) and RDS/MSK throughput were sized
  for web-only traffic. Combined web + native load should be re-checked
  once Phase 1 closed testing brings real device traffic — Phase 0 sideload
  volumes are negligible and don't warrant a re-baseline yet.
- **LLM token cost**: unit cost per conversation is unchanged by *which*
  client started it (same T-01 intent path, same BFF). Total token spend
  only rises if native brings **additional** users/conversations beyond
  what the web client already drives — that number is **Unknown** without a
  user-acquisition forecast, which is outside this skill's domain (that's
  `@aea-product-owner` / sponsor territory, not FinOps).

**Bottom line:** Slices A–C (docs + Phase 0 scaffold) carry no material new
cloud cost. The one real, named cost is the $25 Play account the sponsor is
already covering. Everything else is either free-tier tooling or "revisit
once real traffic exists," not a number to commit to today.

## Architecture — HLD (`@aea-devsecops-platform`)

**Honesty flag:** this is a **proposed** system context, not an implemented
one. No native client exists yet; the boxes below describe what Phase 0
would talk to if built exactly per the ADRs proposed above (not yet
written).

```
                     ┌───────────────────────────────────────────┐
                     │   Unified Session State (PostgreSQL)       │
                     │   Shared Understanding + Cart + Selection  │
                     └─────────────────────┬───────────────────────┘
                                            │
              ┌─────────────────┬──────────┴──────────┬─────────────────┐
              ▼                 ▼                      ▼                 
   Desktop Web (≥1024px)   Mobile Web (<768px)   Android Native (proposed)
   8-Tile Workspace        3-Stage Need→Pick→Pay  Same 3-Stage flow,
   (existing, shipped)     (existing, spec'd,     Compose UI (Figma
                            CF-054: not yet        prototype only —
                            matching spec on       no code yet)
                            live phone)
              │                 │                      │
              └─────────────────┴──────────┬───────────┘
                                            ▼
                     ┌───────────────────────────────────────────┐
                     │   AWS ALB (ACM TLS) — public entry          │
                     └─────────────────────┬───────────────────────┘
                                            ▼
                     ┌───────────────────────────────────────────┐
                     │   Gateway (ADR-007 sole public entry)       │
                     │   ECS Fargate — ALREADY DEPLOYED (aea-pilot)│
                     └─────────────────────┬───────────────────────┘
                                            ▼
                     ┌───────────────────────────────────────────┐
                     │   BFF (edge/) — session, CSRF, projection   │
                     │   No psycopg/Kafka import (ADR boundary)    │
                     └─────────────────────┬───────────────────────┘
                                            ▼
                     ┌───────────────────────────────────────────┐
                     │   Platform orchestration (modular monolith) │
                     │   Domain services execute; agents prepare   │
                     │   (ADR-016)                                 │
                     └───────┬───────────────────────┬─────────────┘
                              ▼                       ▼
                  ┌───────────────────┐   ┌───────────────────────┐
                  │ RDS PostgreSQL 16  │   │ MSK Kafka (TLS/SASL)   │
                  │ event outbox, SoT  │   │ external broker        │
                  └───────────────────┘   └───────────────────────┘

   External, client-side only — NOT inside the AWS trust boundary:
   ┌───────────────────────────────────────────────────────────┐
   │ Firebase (Crashlytics, App Distribution, FCM — Android)     │
   │ Client telemetry + internal distribution only.               │
   │ No PII crosses (NFR-017) — crash reports carry device/stack   │
   │ traces, not session content.                                  │
   └───────────────────────────────────────────────────────────┘
   ┌───────────────────────────────────────────────────────────┐
   │ Google Play Console — distribution channel only (Phase 1+,   │
   │ blocked on account activation). Not in the request path.     │
   └───────────────────────────────────────────────────────────┘
```

**Key HLD statement:** the native app is a **third presentation of one
session**, not a new backend. It authenticates and talks to the exact same
Gateway → BFF → platform chain the two web presentations already use — this
is the literal meaning of product-vision.md's "consuming identical BFF
endpoints without backend rewrites" line, drawn out as a diagram.

## Architecture — LLD (`@aea-devsecops-platform` + `@aea-senior-software-engineer`)

**Honesty flag:** describes the **proposed** internal structure of the
not-yet-built Phase 0 Android scaffold (item 5 in the plan above). Nothing
below exists as code.

**Proposed Android app module layout:**

```
app/
├── ui/                    Jetpack Compose screens
│   ├── NeedScreen.kt          T-01/T-02 — mirrors Figma frame 1
│   ├── PickScreen.kt          T-03/T-04/T-05 — mirrors Figma frames 2–5
│   └── PayScreen.kt           T-06/T-07/T-08 — mirrors Figma frames 6–8
├── state/                 ViewModel + UI state (mirrors Shared Understanding)
├── network/
│   ├── ApiClient.kt           Generated from the BFF's existing OpenAPI
│   │                          contract (ADR-008) — no hand-written models
│   └── SessionInterceptor.kt  Attaches the session reference, not a password
├── session/
│   └── SessionStore.kt        EncryptedSharedPreferences / DataStore,
│                               Keystore-backed — session reference only,
│                               never raw PII/PAN (NFR-017, ADR-013)
├── background/
│   └── TrackingPollWorker.kt  WorkManager — polls T-08 status
├── push/                  (Phase 2+, gated behind the push ADR — not built)
│   └── FcmReceiver.kt
└── telemetry/
    └── CrashReporter.kt       Firebase Crashlytics wrapper — device/stack
                                 traces only, no session content
```

**Proposed request sequence — J1 Urgent Sam, "Find My Bouquet" tap:**

```
Compose UI (NeedScreen)
   │  user taps primary CTA
   ▼
ViewModel — reads local UI state, no business logic here
   │
   ▼
ApiClient (generated client, ADR-008 contract)
   │  attaches session reference (SessionStore), not credentials
   ▼
HTTPS/TLS ── AWS ALB (ACM) ── Gateway (ADR-007 sole entry) ── BFF
   │
   ▼
Platform orchestration — same domain services the web client already hits
   │  fail-closed inventory check (NFR-009), same Available/Unavailable
   │  logic the Figma "Recommendations" screen already reflects
   ▼
RDS (event outbox) + MSK (domain events) — Shared Understanding updates
   │
   ▼
Response ── BFF ── Gateway ── ALB ── ApiClient ── ViewModel
   │
   ▼
Compose UI recomposes — PickScreen renders, same session, same data
the web client would show for the identical input
```

**What this sequence deliberately does NOT show:** no native-only backend
call, no native-only business logic, no duplicate inventory/pricing check.
Any LLD that adds one of those would be flagged as a competing architecture
under the "fit existing ADRs" constraint both `@aea-senior-software-engineer`
and `@aea-devsecops-platform` operate under.

## Summary

Building the Figma concept for a native Android/iOS companion surfaced a gap:
[product-vision.md](../../docs/01-product-vision/product-vision.md#L26) already
names the native vision (*"Android Kotlin/Jetpack Compose leading to iOS
SwiftUI, consuming identical BFF endpoints without backend rewrites"*) but
nothing downstream of that one line exists yet — no ADRs, no native UX spec,
no toolchain decision. This note captures what documentation and tooling
would need to exist before a real native build could start, so a future
session (or human) doesn't have to rediscover the gap.

**Status change 2026-08-29**: sponsor-directed to proceed (see decision log
above). No new FR/US/BG/NFR IDs are introduced — this activates the existing
product-vision.md bullet as a new *delivery surface* for already-approved
requirements, it does not add new product requirements.

## Team response — vision, mission, implementation possibilities, challenges

### Vision & mission (`@aea-product-owner`)

**Go/no-go: Accept.** Evidence: explicit sponsor direction (2026-08-29) plus
the standing vision bullet at
[product-vision.md:26](../../docs/01-product-vision/product-vision.md#L26).
No archive/xlsx change needed — Android and iOS clients consume the *same*
BFF endpoints and the *same* FR/NFR coverage the web client already
implements (FR-001, FR-003, FR-007, FR-008, FR-009, FR-016..019; NFR-005,
NFR-009, NFR-017 among others). This is a new **client surface**, not new
**product scope**.

- **Vision**: one AEA session, presented natively on the device the customer
  already carries — same conversational discovery, same Shared
  Understanding, same fail-closed inventory and zero-PII checkout the web
  client guarantees today, at native speed and with native affordances
  (push, biometric unlock of a saved destination reference, home-screen
  presence).
- **Mission (this phase)**: ship a *thin, honest* Android client — J1–J4
  parity, no feature invented beyond what the BFF already serves — gated by
  its own named milestone and its own UX spec, not a scaled-down copy of the
  desktop workspace (the CF-054 mistake, avoided deliberately this time).
- **Scope discipline**: iOS is sequenced, not parallel. M12 CRM push
  reminders (FR-016) stay out of Phase 0/1 — push infra is a separate ADR
  (see System documentation, below) and a separate milestone slice.
- **Recommended roadmap action**: add a named milestone —
  `M19 — Native Mobile Companion, Android (Reference Extension)` — to
  [roadmap.md](../../docs/07-roadmap/roadmap.md), scoped to J1–J4 parity on
  Android only. This gives `@aea-project-manager` a named milestone to
  assign bench work from (PM cannot pull-forward *unscoped* work). **Not
  applied yet** — flagging for explicit confirmation before editing
  canonical `docs/`.

### Implementation possibilities (`@aea-senior-software-engineer`)

Two viable paths, not mutually exclusive — recommend running Path A as the
build target with Path B as a fallback if Play activation drags on:

| Path | What it is | Fit for "gradual, Android first" |
|---|---|---|
| **A — True native (Compose)** | Kotlin + Jetpack Compose app per product-vision.md's own stated direction; generates its API client from the BFF's existing OpenAPI contract (ADR-008) | Matches the stated vision exactly; best long-term store presence and native UX; slower first milestone |
| **B — WebView/TWA wrapper (interim)** | Android Trusted Web Activity wrapping the existing responsive dual-viewport mobile client (already spec'd) as an installable, push-capable Android app | Fastest possible "Android first" step; reuses 100% of shipped web UI; explicitly a bridge, not the target architecture — would need an explicit sunset plan so it doesn't become permanent by default |

Architecture constraints that hold regardless of path (fit existing ADRs,
not a competing architecture):

- **Gateway stays the sole public entry** (ADR-007) — the native app talks
  to the same edge gateway the web client does, not a new backend.
- **Contract-first** (ADR-008) — no hand-maintained native API models;
  generate from the published schema.
- **Session, not login** — the web client's session-reference pattern
  (no password) carries over; native stores the reference in
  Keystore/Keychain, never raw credentials (NFR-017).
- **Fail-closed inventory, ASO "not a person" disclaimer, destination
  reference not raw address** (ADR-013) all carry over unchanged — the
  Figma prototype already reflects this.

Phasing that works whether or not the Play account activates on time:

1. **Phase 0 — Internal validation.** APK sideload or Firebase App
   Distribution. No Play Console account required. Validates the generated
   API client against the live BFF and the J1 happy path only.
2. **Phase 1 — Closed testing track.** Requires the Play Developer account
   (see blocker, below). J1–J4 parity, real device matrix.
3. **Phase 2 — Public release.** Store listing, phased rollout percentage,
   crash-rate gate before iOS work starts.

### Challenges (`@aea-project-manager`)

**Blockers first:**

| Blocker | Owner | Blocks | Wait tag |
|---|---|---|---|
| Google Play Developer account was the named blocker; validated 2026-08-31 | Sponsor (done) | Remaining: first `.aab` + SHA-1 + closed-track install ([#347](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/347)) — does not block Phase 0 (sideload/Firebase) | `user` (keystore / first Play upload if Console requires Google login) |
| No named milestone yet (M19 not added to roadmap.md) | `@aea-product-owner` | Any bench assignment — PM cannot pull-forward unscoped work, only prep for a *named* milestone | `main`-adjacent process gate, not a stakeholder wait tag |
| No ADRs yet for native client architecture, mobile session/auth, or push | `@aea-senior-software-engineer` (draft) → review | Any code landing, even Phase 0 — "fit existing ADRs" means these get written *before* the first native commit, not after | — |

**On the bench:** no stakeholder currently holds an in-flight native-mobile
issue — there is no GitLab issue yet (confirmed: `glab issue list --search
"mobile"/"native"/"android"` returns none). Until M19 is named and a first
issue opened, this is `no-assignment`, not blocked work.

**Sequencing risk:** "gradual, Android first" only holds if iOS work is
explicitly held, not just implied — recommend PM state that explicitly at
the next cadence slot so no specialist starts iOS prep under pull-forward
rules.

**Process requirement unchanged:** one GitLab issue → one branch from
updated `origin/main` → one MR, same as every other lane. Docs-only ADR/UX
spec work needs no Docker integration; once Android code lands under
`edge/` or a new `mobile/` surface, the Docker-integration-before-MR rule
applies to whatever it touches.

## Evidence

- [product-vision.md §Multi-surface & native mobile vision](../../docs/01-product-vision/product-vision.md#L24-L27) — the only existing canonical statement; explicitly marks native binaries as unimplemented.
- [docs/05-ux-design-guide/path-b-dual-viewport-specification.md](../../docs/05-ux-design-guide/path-b-dual-viewport-specification.md) — the responsive-web mobile spec (Need→Pick→Pay, T-01..T-09) the native screens were translated from.
- [2026-08-27-path-b-dual-viewport-ux-loop-j1-j4.md](2026-08-27-path-b-dual-viewport-ux-loop-j1-j4.md) — J1–J4 journey definitions and the honest findings (dual CTA, gated Track/Contact Florist, ambiguous budget chips) the native screens had to account for.
- Figma prototype (this session): 10 frames — cover/legend, J1 Need·Conversation, Pick·Recommendations (J1/J3 reorder badge), J2 Pick·Customize, Pick·Delivery, Pay·Order Summary, Pay·Checkout, Pay·Tracking (unlocked), J4 gated Track/Contact-Florist state, J4 ASO bottom-sheet overlay. Palette reused verbatim from `edge/gateway/ui/assets/styles.css` (not invented).

## 1. System documentation needed

None of these exist today. Proposed net-new documents, each parallel to an
existing doc this repo already has for the web client:

| Proposed doc | Parallels | Why it's needed before code |
|---|---|---|
| Native Mobile UX Specification | `docs/05-ux-design-guide/path-b-dual-viewport-specification.md` | Screen map + native-idiom translations (segmented control not CSS progress bar, bottom sheet not modal drawer, platform date/payment sheets) — the Figma file above is a first draft, not this doc. |
| ADR: Native client architecture | ADR-002/003 (workspace architecture) | Records the "one BFF, two native clients, no backend rewrite" decision from product-vision.md as an actual ADR with consequences, not a single vision-doc line. |
| ADR: Mobile session & auth model | ADR-013 (destination reference, no raw address) | How the web's session-cookie/no-login pattern maps to Keychain (iOS) / EncryptedSharedPreferences or DataStore (Android); confirms NFR-017 zero-PII carries over to native storage, not just native network calls. |
| ADR: Native push & proactive engagement | FR-016 (`EngagementCrmService`) | product-vision.md already flags FCM/APNs relays as unshipped; needs a decision record before any push code exists, since push is a new class of unsolicited-contact risk this repo hasn't governed yet. |
| Native release & distribution doc | (none yet) | App Store / Play Console submission, code signing, and how native app versioning ties to BFF contract versioning (ADR-008 Contract-First API) so a native release can't silently drift from the contract. |
| Native observability doc | `docs/observability` (Grafana dashboards) | Crash reporting and mobile-equivalent performance budget (cold start, frame drops) parallel to `@aea-performance-guardian`'s LCP work — tool choice not yet decided, only the need is clear. |
| Native journey walker scripts | `scripts/walk_returning_shopper.py` | J1–J4 need a native equivalent to the existing Playwright-based web walker so CF-054-style honest re-probing works on native, not just web. |
| ASO parity note | FR-009 (fail-closed, "not a person") | One paragraph confirming the ASO disclaimer and fail-closed behavior shown in the Figma overlay screen is a hard carry-over requirement, not a native reinterpretation. |

## 2. Toolset / toolkit

Not yet decided — this is what *would* need deciding, grouped by what's
already fixed by existing ADRs vs. genuinely open:

**Fixed by existing architecture (ADR-008 Contract-First API):**
- Both native clients generate from the same OpenAPI contract the web BFF already publishes — no parallel backend, no hand-maintained native API models.

**Android (open, but conventional given Kotlin/Compose is already named in product-vision.md):**
- Kotlin, Jetpack Compose, Coroutines/Flow
- Retrofit or Ktor client generated from the shared OpenAPI contract
- DataStore for the session reference (not raw credentials — NFR-017)
- WorkManager for background tracking polls
- Firebase Cloud Messaging for push
- Compose UI Testing / Espresso for the native journey walkers

**iOS (open, but conventional given SwiftUI is already named):**
- Swift, SwiftUI, async/await
- A generated client from the same OpenAPI contract (or URLSession directly)
- Keychain Services for the session reference
- APNs for push
- XCTest/XCUITest for the native journey walkers

**Cross-cutting, genuinely undecided:**
- Crash/observability SDK feeding the same Grafana instance this repo already runs (`aea-pilot` on ECS Fargate) — vendor not chosen.
- Release automation (Fastlane is the conventional choice for both stores but isn't decided here).
- Design→code parity tooling: the Figma MCP server already ships a `figma-swiftui` skill (bidirectional SwiftUI ⇄ Figma) that could keep the iOS screens in sync once real SwiftUI views exist; there is no equivalent first-party Code Connect path for Compose today, so Android design→code parity would stay manual or need a custom mapping.

## Proposed canonical targets

| Path | Change type | Notes |
|------|-------------|-------|
| `docs/06-adr/ADR-0NN-native-client-architecture.md` | add | Needs an actual ADR number assigned at promotion time, not here. |
| `docs/06-adr/ADR-0NN-mobile-session-auth.md` | add | Same. |
| `docs/05-ux-design-guide/native-mobile-ux-specification.md` | add | Would formalize the Figma prototype's screen map. |
| `docs/01-product-vision/product-vision.md` | clarify | Optional: link forward to the new ADRs once they exist, instead of the current single unlinked bullet. |

## ID impact

- [x] None (prose / structure only) — no FR/US/BG/NFR IDs invented or implied.
- [ ] Cites existing BG/US/FR/NFR IDs only
- [ ] Would require archive/xlsx change (stop — escalate explicitly)

## Risks / open questions

- Native mobile is Future-extension scope (M14–M18 territory per the daily brief's milestone labels) — promoting the ADRs before there's a scheduling decision could read as commitment that hasn't been made. Flag to `@aea-product-owner` before promoting.
- The Figma prototype is a concept walkthrough (hand-styled frames), not a production component library — if this gets greenlit, rebuilding it via the `figma-generate-library` skill (real variables, variants, component states) is a separate, larger pass.
- No video was produced for J1–J4 on native — no video-rendering tool was available this session; the Figma prototype's click-through flow (Need → Pick → Customize → Delivery → Order Summary → Checkout → Tracking, plus the gated-state branch back to Checkout) is the closest substitute, screen-recordable by a human.

## Ready for promote?

- [x] Does not invent requirement IDs
- [ ] Owner path identified — needs `@aea-product-owner` (scope/timing) and `@aea-ux-designer` (UX spec ownership) sign-off before this moves past candidate.
- [ ] Coherence SOP needed? No — this isn't a coherence finding (nothing here contradicts published docs), it's a scope proposal.
