# Play API CI upload for internal / closed testing (#354)

> **Tags**: #aea #second-brain #native-mobile #ci #play #secrets
> **Captured**: 2026-09-02
> **Owners**: `@aea-devsecops-platform` (implement) · sponsor pastes SA JSON CI var
> **Traceability**: GitLab #354 · feeds from #347 `android-bundle-release` · App Distribution honesty pattern from #363

Inherits [[2026-09-01-android-upload-keystore-gitlab-file-var]] and the Android
companion README Play sections. Native push stays [[ADR-019]]. Milestone [[M19]].

## Why this note exists

Sponsor unparked automation 2026-09-02 after a manual closed/internal `.aab`
was accepted on Play. The next honesty step is CI → Play API for the same
track — not browser upload forever. Agents must not invent secrets or ask the
sponsor to paste service-account JSON in chat.

## What shipped (scaffold)

- Script: `scripts/upload_play_aab.py` — dry-runnable; real path uses
  `google-api-python-client` edits → bundles.upload → tracks.update → commit.
- Offline tests: `scripts/test_upload_play_aab.py`.
- Manual CI job: `android-play-internal-upload` (allow_failure; omitted when
  `PLAY_API_SERVICE_ACCOUNT_JSON` unset — same pattern as App Distribution).
- Default API track: `internal`. Override `PLAY_TRACK` for closed-testing’s
  Console API name (`alpha` / custom). **Production forbidden** in script.
- Docs: `clients/mobile/android/README.md` names the var and sponsor steps
  (Play Console grant + GitLab File var) without secret values.

## Variable name (only)

| Variable | Type | Notes |
|---|---|---|
| `PLAY_API_SERVICE_ACCOUNT_JSON` | File, Protected | Play Developer API SA JSON. Never artifact. Never commit. Never paste in issues/MRs/chat. |

Sibling signing vars unchanged: `ANDROID_UPLOAD_KEYSTORE` (base64 File),
`ANDROID_UPLOAD_KEYSTORE_PASSWORD`, `ANDROID_UPLOAD_KEY_ALIAS`,
`ANDROID_UPLOAD_KEY_PASSWORD`, plus `GOOGLE_SERVICES_JSON`.

## Residual sponsor steps

1. Create / confirm Play API service account with release rights on this app’s
   internal/closed track only.
2. Paste JSON into GitLab CI/CD → Variables as `PLAY_API_SERVICE_ACCOUNT_JSON`
   (Type File, Protected).
3. Confirm API track name if not `internal` → set `PLAY_TRACK`.
4. Bump `versionCode` before each new upload (Play rejects duplicates).
5. On protected `main`, play `android-bundle-release` then
   `android-play-internal-upload` and record versionCode + date on #354.

## Honesty

Wiring ≠ upload success until the File var exists and a commit edit lands.
Internal/closed ≠ Production. App Distribution ≠ Play install path.
