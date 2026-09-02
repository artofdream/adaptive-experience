# Android companion (M19)

Local Firebase config is **not** in git. Copy the real file from the Firebase
console next to this README's example:

`app/google-services.json.example` → `app/google-services.json`

Never commit `google-services.json`. `git check-ignore -v app/google-services.json`
must report the repo-root `.gitignore` rule.

## CI delivery

GitLab CI injects the live file as a **protected file variable** named
exactly `GOOGLE_SERVICES_JSON`. The job copies that file to
`app/google-services.json` in the job workspace only. Do not attach it as a
pipeline artifact. Do not paste the JSON into issues, MR notes, or research
files.

If `GOOGLE_SERVICES_JSON` is absent, `android-build-debug` copies
`app/google-services.json.example` so assemble still compiles. That dummy
cannot talk to the live Firebase project.

**Remaining sponsor step:** paste the live `google-services.json` into GitLab
CI/CD → Variables as a **protected, masked file** variable named
`GOOGLE_SERVICES_JSON`. Do not create that variable from an agent. Do not
commit the live file.

Crashlytics and App Distribution Gradle plugins are wired. No FCM / push
(ADR-019). Key restriction or rotation stays on #321 as date + package
only — no key values.

## Signed Play App Bundle (closed testing, #347)

CI job `android-bundle-release` runs Gradle `bundleRelease` for package
`link.artof.aea.companion` and artifacts `app-release.aab` only. Debug APKs
stay debug-signed as today. This is not a production track.

The job is **manual** with `allow_failure: true`. It is listed on Android /
`.gitlab-ci.yml` MRs and on `main` (including web pipelines). It is **not**
an MR gate. **Protected** CI variables are typically not injected on
unprotected MR source branches — do not expect this job to produce an `.aab`
on every MR. The job is created only when `$ANDROID_UPLOAD_KEYSTORE` is set
in that pipeline; otherwise it is omitted (not a skip-green). Job result is
Unknown until a run with sponsor-pasted secrets produces the artifact. Play closed-track install
and Play App Signing SHA-1 in Firebase remain Unknown until a tester can
install from the closed track.

Release `signingConfig` reads these env vars **only when all are set**:

- `ANDROID_UPLOAD_KEYSTORE` — GitLab **file** variable; **base64 of the JKS**
  (not raw binary). The job `base64 -d`s it to a job-local keystore for Gradle.
- `ANDROID_UPLOAD_KEYSTORE_PASSWORD`
- `ANDROID_UPLOAD_KEY_ALIAS`
- `ANDROID_UPLOAD_KEY_PASSWORD`

Sponsor re-paste of `ANDROID_UPLOAD_KEYSTORE` as base64 is recorded 2026-09-01
(#351). Do not recreate `GOOGLE_SERVICES_JSON`. Do not commit a keystore, PEM,
or SHA-1. Do not paste values in issues, MRs, or chat.

## Play API upload (internal / closed testing, #354)

CI job `android-play-internal-upload` uploads the signed `app-release.aab` to
Play **internal** testing (API track `internal`) via the Google Play Android
Developer API. Closed testing uses the Console track’s API name (often
`alpha` or a custom track) — set optional CI variable `PLAY_TRACK` after
confirming in Play Console. **Never** Production.

The job is **manual** with `allow_failure: true`. It is **omitted** when
`PLAY_API_SERVICE_ACCOUNT_JSON` is unset (same honesty as App Distribution /
`android-bundle-release`). It prefers the `android-bundle-release` artifact;
if the `.aab` is missing it rebuilds with the existing `ANDROID_UPLOAD_*`
signing vars. Offline unit tests: `python scripts/test_upload_play_aab.py -v`.
Dry-run (no Google calls): `python scripts/upload_play_aab.py --dry-run`.

### Required GitLab CI variable (sponsor)

| Variable | Type | Notes |
|---|---|---|
| `PLAY_API_SERVICE_ACCOUNT_JSON` | **File**, Protected | Play Developer API service-account JSON. Never artifacted. Never commit. Never paste in issues/MRs/chat. |

Optional: `PLAY_TRACK` (default `internal`), `PLAY_RELEASE_STATUS` (default
`completed`), `PLAY_PACKAGE_NAME` (default `link.artof.aea.companion`).

### Sponsor: attach SA in Play Console + GitLab (no secrets in chat)

1. Play Console → **Users and permissions** / **API access** → link a Google
   Cloud project → create a **service account** (or reuse one) with permission
   to release to this app’s **internal / closed** track only (not Production).
2. In Google Cloud → IAM → service account → Keys → Add key → JSON. Download
   stays on the sponsor machine only.
3. GitLab → Settings → CI/CD → Variables → **Add variable**:
   - Key: `PLAY_API_SERVICE_ACCOUNT_JSON` (exact name)
   - Type: **File**
   - Protected: **on**
   - Masked: off (File variables are not masked)
   - Value: paste the JSON into the textarea (GitLab has no binary picker)
4. Do **not** paste the JSON into issues, MRs, chat, or research notes.
5. On `main` (protected branch so the var injects), run **manual**
   `android-bundle-release`, then **manual** `android-play-internal-upload`
   (or let the upload job rebuild if the artifact is absent).

### versionCode bump policy

Play rejects an upload when `versionCode` is not greater than the last
accepted bundle on that app. Bump `versionCode` in
`clients/mobile/android/app/build.gradle.kts` before each new API upload.
A failed duplicate-code edit is an honest fail — not a green skip.

### Honesty

- Job wiring ≠ successful Play upload until the sponsor var exists and a
  pipeline run commits an edit.
- Internal/closed API upload ≠ Production.
- App Distribution / debug APK ≠ Play install path.

Vault: [`research/random-thoughts/2026-09-02-play-api-ci-upload-closed-testing.md`](../../../research/random-thoughts/2026-09-02-play-api-ci-upload-closed-testing.md).

## Native↔web parity (gap-closing loop)

Living matrix + detect→decide→ship→prove loop:
[`research/random-thoughts/2026-09-02-companion-native-web-gap-closing-loop.md`](../../../research/random-thoughts/2026-09-02-companion-native-web-gap-closing-loop.md).
MVP sequence: contract tests (#367) → `X-AEA-Client` (#368) → weekday probe (#369) (script + CI job).
Public page: [architecture.artof.link/companion](https://architecture.artof.link/companion).
Dual-probe honesty remains #360. App Distribution ≠ Play. T-09 operator ≠ orders.

### BFF contract tests (#367)

`android-build-debug` runs `testDebugUnitTest`, including `BffWebContractTests` plus
golden JSON under `app/src/test/resources/bff_golden/` (web `confirmAndPay` shapes).
CI fails on native↔web drift classes: product-only `observed_total` (pre-!379) and
Start Over without `clearSessionState` before `createSession` (pre-!380). Unit
fixtures ≠ live dual-probe (#360) and ≠ weekday API probe (#369).

### `X-AEA-Client` Grafana channel (#368)

Observability only — **not** auth. Same public Bearer (`local-browser-token`) remains.

| Client | Header |
|--------|--------|
| Android companion (`BffClient`) | `X-AEA-Client: companion-android` |
| Web shop / florist UI (`app.js`, `florist.js`) | `X-AEA-Client: web` |

Edge nginx forwards the header on `/api/` and writes `aea_client="$http_x_aea_client"` in access logs. BFF allowlists `companion-android` / `web` (else `unknown`), echoes `X-AEA-Client` on responses, and emits JSON `bff_access` lines with field **`aea_client`** (plus `unspecified` when absent).

**Operator label (CloudWatch Logs Insights / Grafana):** `aea_client`  
Log group: `/aea/aea-pilot/bff`. Example:

```
fields @timestamp, aea_client, status, path, method
| filter event = "bff_access"
| stats count(*) as requests by aea_client, status
```

**As-code panels** (uid `aea-unified-dashboard`): **BFF requests by aea_client (X-AEA-Client)** (timeseries) and **BFF aea_client × status (table)** in `platform/docker/grafana/provisioning/dashboards/aea_unified_dashboard.json`. Honesty: **query documented / panel as-code** — live series need edge/BFF+Grafana redeploy + traffic. Vault: `research/random-thoughts/2026-09-02-x-aea-client-grafana-label.md`.

### Weekday / CI API parity probe (#369)

Script: [`scripts/probe_companion_bff_parity.py`](../../../scripts/probe_companion_bff_parity.py).
Mirrors companion `BffClient` against live Path B (`https://aea.artof.link`, or
`AEA_BFF_BASE_URL` / staging origin when documented): cookie jar + CSRF,
`X-AEA-Client: companion-android`, Need→Pick→Pay through checkout with
`observed_total` from workspace `order_summary.total` after delivery.

**Run locally:**

```bash
python scripts/probe_companion_bff_parity.py
# optional: --base-url https://aea.artof.link --json-out /tmp/parity.json
python scripts/test_probe_companion_bff_parity.py -v   # offline helpers only
```

**CI job** `companion-bff-parity-probe` (manual on MRs / main web; schedule when
`CI_PIPELINE_SCHEDULE_DESCRIPTION` contains `Companion BFF parity probe`, or
optional `AEA_COMPANION_PARITY_PROBE=1`). Failures exit non-zero and print
correlation ids — they do **not** auto-open GitLab issues. Confirmed drift →
one finding issue (one finding → one MR); comment on #360 only when dual-probe
related.

Weekday schedule (sponsor / maintainer): GitLab → CI/CD → Schedules → description
**Companion BFF parity probe (weekday)**, cron `0 6 * * 1-5` Europe/Berlin on
`main`. No schedule-scoped Variables required (GitLab UI Edit schedule may only
show Inputs). Job matches on schedule description so the daily brief schedule
does not fire the probe. Optional `AEA_COMPANION_PARITY_PROBE=1` remains as a
fallback OR.

**Honesty:** probe green ≠ Play honesty gate; ≠ operator / website write-through
(#360 still open); T-09 sample operator ≠ live orders. Do not claim dual-probe
write-through from this job.

## Live BFF wiring (internal testing, #362)

Need / Pick / Pay call the live Edge BFF at `https://aea.artof.link` (cookie
session + `X-CSRF-Token`, conversation `message_text`, selection/delivery/order/
checkout). The local Mom-keyword mock path that unlocked occasion without BFF
shared-understanding is **removed**.

- Sponsor scope: **internal testing only** (not a public Play production claim).
- Demo mock happy-path for Need chat is removed on the wired path.
- Catalog may still use a local fallback list (with sold-out fail-closed) when
  workspace recommendations are unavailable; selection/checkout still POST to BFF.
- Checkout sends opaque `session_pay_ref` only — no raw card fields (ADR-013).
- Do not claim website/operator dual-write until sponsor re-probes (dual-probe
  still required; #360). Debug / App Distribution builds do **not** prove
  operator write-through.
- CORS is N/A for the native client; residual risks include mobile cookie/`__Host-`
  CSRF handling and payment_reference source (session vault ref, not a card vault SDK).

### UX / BFF hardening (#365)

- **Back-nav + Start Over:** Pick → Need (clears selection), Pay → Pick; Start Over
  on Need / Pick / Pay (not only Tracking) via existing `startOver()`. Stage
  progress remains non-clickable.
- **Checkout totals:** `completeCheckout` refreshes workspace and posts
  `observed_total` from `facets.order_summary.total` (product + delivery fee),
  matching web `confirmAndPay` — not product-only price (avoids `total_mismatch`
  409 after delivery fee is applied).
- **409 copy:** `stale_context` / `total_mismatch` / `checkout_conflict` /
  `product_unavailable` map to distinct user-facing messages. Selection/delivery
  get a **one-shot** `stale_context` retry after adopting `context_version`;
  `product_unavailable` is not auto-retried forever.
- **Start Over session reset (#366):** `startOver()` calls `BffClient.clearSessionState()`
  (cookie jar + CSRF) before `createSession`, then refreshes shared-understanding —
  BFF reuses `__Host-aea_*` cookies on POST `/session`, so without clear the next
  Need message posts `observed_context_version: 0` against the old live session (409
  `stale_context`). Conversation posts also get a one-shot `stale_context` retry.

## UX validation loop

Fast Need/Pick/Pay review **without** waiting on every Play Console AAB upload.
Tracked in [#363](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/363) (A/B) and [#364](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/364) (Phase C screenshots).
Design note + checklist:
[`research/random-thoughts/2026-09-02-companion-ux-online-validation-setup.md`](../../../research/random-thoughts/2026-09-02-companion-ux-online-validation-setup.md).

### Debug APK from CI (Phase A)

1. Open the MR / `main` pipeline that ran `android-build-debug` (triggers on
   changes under `clients/mobile/android/**` or `.gitlab-ci.yml`).
2. Job artifacts include the debug APK path:
   `clients/mobile/android/app/build/outputs/apk/debug/app-debug.apk`
   (expire_in 14 days).
3. Download `app-debug.apk`, sideload (`adb install -r …`) or use an emulator.
   This build is **debug-signed**, not Play App Signing.

### Sponsor devices today

- **scrcpy** (USB) and **Play internal testing** remain how the sponsor
  captures screenshots and validates the **store install path**.
- Play internal is the honesty gate for “installs from Play”. App Distribution
  and debug APKs do **not** replace that gate.

### Firebase App Distribution (Phase B)

Gradle plugin `com.google.firebase.appdistribution` is already applied. CI job
`android-app-distribution` runs **manual** with `allow_failure: true`, and is
**omitted** when the service-account file variable is absent (same honesty
pattern as `android-bundle-release`).

Sponsor / DSO (do **not** commit secrets; do **not** paste JSON in issues):

1. Firebase Console → App Distribution → create group **`ux-testers`** (or
   set `FIREBASE_APP_DISTRIBUTION_GROUPS`).
2. Add UX hat + sponsor emails to that group.
3. Create a Google Cloud service account with Firebase App Distribution Admin,
   download JSON key.
4. GitLab CI/CD → Variables → **protected file** variable
   `FIREBASE_APP_DISTRIBUTION_CREDENTIALS` = that JSON (job copies to a
   workspace path only; never artifacted).
5. Optionally keep `GOOGLE_SERVICES_JSON` as today so the job can assemble with
   the real Firebase client.
6. Run `android-app-distribution` manually on a pipeline where the variable is
   injected. First successful tester invite/upload stays **Unknown** until that
   run succeeds — do not claim green distribution from wiring alone.

### Paparazzi Compose screenshots (Phase C, #364)

Optional JVM screenshot path — **no emulator / Maestro** in this increment
(Maestro remains deferred; disproportionate for the first Phase C MR).

1. Open an MR / `main` pipeline that lists job **`android-compose-screenshots`**
   (changes under `clients/mobile/android/**` or `.gitlab-ci.yml`).
2. Run the job **manually** (`allow_failure: true` — does not gate main).
3. Download artifacts: Paparazzi PNGs under
   `clients/mobile/android/app/src/test/snapshots/` (plus reports).
4. Studio: `@Preview` surfaces in
   `app/src/main/.../ui/preview/CompanionScreenPreviews.kt` (Need / Pick / Pay).

Gradle locally (needs Android SDK):

```bash
cd clients/mobile/android
sh ./gradlew :app:recordPaparazziDebug   # write PNGs for review
# later: sh ./gradlew :app:verifyPaparazziDebug  # when goldens are committed
```

Screenshots are for fast UX review only. They are **not** the Play store
install path and **not** dual-probe evidence.

### Honesty

- **Play internal** remains the honesty gate for “installs from Play”. Debug
  APK, App Distribution, and Paparazzi screenshots do **not** replace that gate
  (#354 automates AAB→Play separately).
- Dual-probe website / operator write-through stays **out of automated CI**
  (manual sponsor probe; #360). Do not wire dual-probe into
  `android-compose-screenshots`.
- Live BFF is wired for internal testing (#362); still score the vault **UX
  checklist** (contrast, back stack, single CTA, FR-009, demo banner honesty,
  budget ask, chip vs free-text unlock) against every review build.
- **Budget ask (#359):** After occasion unlock on Need, companion shows budget
  chips (Under $50 / $50–100 / $100+) plus **Skip**. Choice PATCHes
  `/api/v1/shared-understanding` (web Path B correction). Pick applies a
  **local** `arrangement.price` ceiling filter when a ceiling is set; Pay shows
  budget honesty. Live BFF recommendation re-rank is best-effort via existing
  workspace refresh — not a new API.
