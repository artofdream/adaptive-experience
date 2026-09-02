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

## Native↔web parity (gap-closing loop)

Living matrix + detect→decide→ship→prove loop:
[`research/random-thoughts/2026-09-02-companion-native-web-gap-closing-loop.md`](../../../research/random-thoughts/2026-09-02-companion-native-web-gap-closing-loop.md).
MVP sequence: contract tests (#367) → `X-AEA-Client` (#368) → weekday probe (#369).
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

**Operator label (CloudWatch Logs Insights / Grafana explore):** `aea_client`  
Example filter: `{ $.event = "bff_access" } | stats count(*) by aea_client, status`.  
Repo Grafana dashboards (`platform/docker/grafana/provisioning/dashboards/`) are still CloudWatch **infra** panels — no request-series client split as-code yet (**partial**). Vault: `research/random-thoughts/2026-09-02-x-aea-client-grafana-label.md`.

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
Tracked in [#363](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/363).
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

### Honesty

- No live BFF / website / operator write-through from debug or App Distribution
  builds until #362 is done and dual-probed (#360).
- Score the vault **UX checklist** (contrast, back stack, single CTA, FR-009,
  demo banner until BFF, budget ask, chip vs free-text unlock) against every
  review build.
