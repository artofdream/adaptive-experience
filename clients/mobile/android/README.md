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
on every MR. When the upload-keystore variables are absent the script exits 0
with an honest SKIP (not a signed bundle). Job result is Unknown until a run
with sponsor-pasted secrets produces the artifact. Play closed-track install
and Play App Signing SHA-1 in Firebase remain Unknown until a tester can
install from the closed track.

Release `signingConfig` reads these env vars **only when all are set**:

- `ANDROID_UPLOAD_KEYSTORE` — GitLab **file** variable; Gradle `storeFile`
- `ANDROID_UPLOAD_KEYSTORE_PASSWORD`
- `ANDROID_UPLOAD_KEY_ALIAS`
- `ANDROID_UPLOAD_KEY_PASSWORD`

**Remaining sponsor step:** paste the upload keystore and passwords into
GitLab CI/CD → Variables (do not paste values in issues, MRs, or chat):

- `ANDROID_UPLOAD_KEYSTORE` — File, protected (binary; masking may not apply)
- `ANDROID_UPLOAD_KEYSTORE_PASSWORD` — Variable, protected, masked
- `ANDROID_UPLOAD_KEY_ALIAS` — Variable, protected
- `ANDROID_UPLOAD_KEY_PASSWORD` — Variable, protected, masked

Do not create those variables from an agent. Do not commit a keystore, PEM,
or SHA-1. Same paste pattern as `GOOGLE_SERVICES_JSON`.
