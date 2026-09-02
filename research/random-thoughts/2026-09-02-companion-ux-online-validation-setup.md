# Companion UX online validation setup (Phase A/B/C)

> **Tags**: #aea #second-brain #mobile #companion #ux #ci #honesty #path-b #knowledge-first
> **Captured**: 2026-09-02
> **Issue**: [#363](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/363) (A/B); Phase C: [#364](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/364)
> **Related probe**: [[2026-09-02-android-companion-alpha-probe-mock-vs-bff]] / #361 / !375
> **Sponsor findings**: #357 #358 #359 #360

## Why

Play Console → AAB → internal install is too slow for Need/Pick/Pay UX iteration.
Sponsor keeps personal Play internal testing as the **store-path honesty gate**.
We need a **dedicated fast UX validation loop** (CI debug APK + checklist now;
Firebase App Distribution next; Play automation stays #354).

Honesty: live BFF is wired for internal testing (#362). Do **not** claim
website / operator dual-write or store readiness from debug / App Distribution /
Paparazzi alone — dual-probe (#360) and **Play internal** remain separate honesty
gates. Dual-probe stays out of automated CI.

## Phased shape

### Phase A — Fast visual / sideload loop (this delivery)

1. **Debug APK artifact** from GitLab job `android-build-debug`
   (`clients/mobile/android/app/build/outputs/apk/debug/app-debug.apk`),
   expire_in **14 days**. Sideload / emulator — **not** Play-signed.
2. **UX checklist** (below) scored against sponsor scrcpy / Play screenshots
   and future CI screenshots.
3. Lightweight CI guard `android-ux-checklist` verifies this vault note + the
   companion README **UX validation loop** section exist when android paths
   change.
4. **Paparazzi screenshots** moved to **Phase C (#364)** — landed as
   optional manual CI (`android-compose-screenshots`) + Need/Pick/Pay previews.
   Pages gallery under `/stack` or `ux-companion/` still optional later.

### Phase B — Online device without Play (this delivery, ops may lag)

4. **Firebase App Distribution** — Gradle plugin already present (#308 era).
   CI job `android-app-distribution` uploads a debug (or release-unsigned /
   upload-key) build to a **UX testers** group when the service-account file
   CI variable is present. Manual / omitted when missing — same honesty pattern
   as `android-bundle-release`. Faster than Play internal for iteration; still
   real Android.
5. Maestro / emulator Compose UI smoke (Need chip / Back / Confirm) —
   still optional; deferred in #364 as disproportionate vs Paparazzi JVM path.

### Phase C — Play honesty + optional screenshot CI (this delivery, #364)

6. Keep **Play internal** as the store-install honesty gate (docs + README).
   App Distribution / debug APK / Paparazzi do **not** replace it. AAB→Play
   automation remains #354.
7. **Paparazzi** JVM Compose screenshots for Need / Pick / Pay:
   - Plugin `app.cash.paparazzi` 1.3.5 + `CompanionScreenPaparazziTest`
   - Studio `@Preview` in `CompanionScreenPreviews.kt`
   - CI job `android-compose-screenshots`: **manual** + `allow_failure: true`,
     runs `recordPaparazziDebug`, uploads PNG artifacts (14 days). Does not
     gate main.
8. **Maestro / emulator smoke**: deferred — disproportionate for first Phase C
   MR (cimg emulator image cost). Optional follow-on if Paparazzi gallery is
   insufficient for chip / Back / Confirm interactions.
9. Dual-probe website / operator **remains out of automated CI** (honesty
   #360). Manual sponsor probe only.

## Non-goals

- Replacing sponsor Play internal probes.
- Claiming live agent UX until BFF is wired.
- Full BrowserStack matrix on day one.
- Committing `google-services.json`, service-account JSON, keystores, or `.env`.

## UX checklist (score against screenshots / sideload)

Use sponsor scrcpy findings (#357–#360) and any new debug APK / App Distribution
build. Mark each Pass / Fail / N/A with build id (versionCode / pipeline job /
Play track).

| # | Check | Related | Pass? |
|---|--------|---------|-------|
| 1 | **Contrast** — primary CTA, chips, body text readable on light/dark; disabled CTA clearly disabled (not low-contrast “maybe tappable”) | UX hat; probe screens | |
| 2 | **Back stack** — from Pick, system Back or explicit back returns to Need without trapping the user into a SKU select | #358 | |
| 3 | **Single CTA honesty** — one primary forward CTA per step; label matches what happens (no “Continue” that only works for one chip) | #357 | |
| 4 | **FR-009** — automated-assistant disclaimer visible (`AsoDisclaimer`: “automated florist assistant, not a person (FR-009)”) on Need/Pick/Pay surfaces | FR-009 / Components.kt | |
| 5 | **Demo banner until BFF** — Confirm / Pay copy or banner must not imply live website / atelier / operator write-through while `SessionRepository` checkout is local mock | #360 #362 | |
| 6 | **Budget ask** — Need (or early Pick) prompts for budget or explicit skip; silence is Fail | #359 | |
| 7 | **Chip vs free-text unlock** — Anniversary chip **and** free-text occasion Send unlock Need Continue (not only Mom's Birthday keyword) | #357 | |

### How to grab evidence

1. Pipeline → job `android-build-debug` → download `app-debug.apk` artifact.
2. Sideload (`adb install -r …`) or emulator; optional **scrcpy** for sponsor
   review (still used today).
3. Sponsor **Play internal** remains the store-path check — separate from this
   fast loop.
4. When App Distribution is live: install from Firebase email/link; still score
   this checklist; still re-probe Play before claiming store readiness.

## CI / docs map

| Piece | Location |
|-------|----------|
| Debug APK job | `.gitlab-ci.yml` → `android-build-debug` |
| UX checklist guard | `scripts/check_companion_ux_validation.py` + job `android-ux-checklist` |
| App Distribution job | `.gitlab-ci.yml` → `android-app-distribution` (manual; omit if credentials missing) |
| Paparazzi screenshots | `.gitlab-ci.yml` → `android-compose-screenshots` (manual + allow_failure) |
| Companion README loop | `clients/mobile/android/README.md` → **UX validation loop** |
| This note | `research/random-thoughts/2026-09-02-companion-ux-online-validation-setup.md` |

## Status words (honesty)

- **Phase A docs + debug APK expire_in + checklist guard**: delivered (#363 / !377).
- **Phase B App Distribution Gradle + CI job wiring**: delivered; **first
  successful tester upload**: Unknown until sponsor pastes
  `FIREBASE_APP_DISTRIBUTION_CREDENTIALS` (and `ux-testers` group) — do not
  invent a green upload.
- **Phase C Paparazzi + manual screenshot job + Play honesty docs**: delivered
  in the #364 MR when merged. **First green `recordPaparazziDebug` in CI**:
  Unknown until the manual job is run — do not invent green screenshots.
- **Maestro / emulator smoke**: deferred (optional follow-on).
- **Play internal honesty gate**: unchanged — still required for store install
  claims (#354 for AAB→Console automation).
- **Live BFF**: wired for internal testing (#362). **Dual-probe website /
  operator**: still open (#360) — out of automated CI by design.

## Phase C progress (2026-09-02)

Sponsor unparked Phase C. Stack choice after reading existing android CI:

| Option | Decision |
|--------|----------|
| Maestro + emulator on cimg | Deferred — heavy image / flaky cost for first MR |
| Gradle managed devices | Deferred — same emulator cost class |
| **Paparazzi 1.3.5 JVM screenshots** | **Chosen** — smallest green increment; Need/Pick/Pay |
| Committed golden verify | Later — first job uses `recordPaparazziDebug` + artifacts |

Docs keep Play internal as honesty gate; dual-probe stays manual (#360).
