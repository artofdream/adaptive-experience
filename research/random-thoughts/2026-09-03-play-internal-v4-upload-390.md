# Play internal versionCode 4 uploaded (#390) — device prove still open

> **Tags**: #aea #companion #play #honesty #ci #390 #knowledge-first
> **Captured**: 2026-09-03 ~19:25 Europe/Berlin
> **Owners**: `@aea-devsecops-platform` · `@aea-knowledge-guardian` · sponsor (Play install on device)
> **Related**: [[2026-09-02-play-api-ci-upload-closed-testing]] · [[2026-09-02-asus-play-v3-smoke-native-gaps]] · [#390](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/390) · [!436](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/436)

Two-track: **CI → Play internal v4 succeeded**. **Device still shows debug sideload v3.** Do not conflate.

## Track 1 — Play API (proved)

| Item | Value |
| --- | --- |
| Merge | !436 `05cba306` (`versionCode` 3→4) |
| MR pipeline | [2817542090](https://gitlab.com/artof-group/adaptive-experience-architecture/-/pipelines/2817542090) success |
| Main pipeline | [2817597077](https://gitlab.com/artof-group/adaptive-experience-architecture/-/pipelines/2817597077) |
| `android-bundle-release` | [16289572350](https://gitlab.com/artof-group/adaptive-experience-architecture/-/jobs/16289572350) success |
| `android-play-internal-upload` | [16289572351](https://gitlab.com/artof-group/adaptive-experience-architecture/-/jobs/16289572351) success |
| package | `link.artof.aea.companion` |
| track | `internal` |
| versionCode | **4** |
| release_status | `completed` |
| committed | `true` |
| edit_id | `03348622569212908185` |
| sha1 | `1a2b72f51935c4e46fb34b873c204c54c9a71d5e` |

Do **not** re-play those jobs for this versionCode.

## Track 2 — device (not proved)

Handset for this pass: **SM_A366B** `RZCY60W1EZW` on cts-ai (not ASUS).

Dumpsys after upload (2026-09-03 ~19:24 Europe/Berlin):

- `versionCode=3` / `0.1.0-alpha`
- flags include **DEBUGGABLE**
- `installerPackageName=null`
- `lastUpdateTime=2026-09-02 20:10:34`

adb cannot silently install Play updates. `market://details` did not change dumpsys.

**Sponsor:** install v4 from Play Internal / App Tester on the A36. Opt-in URL recorded on #354 for v3: https://play.google.com/apps/internaltest/4701506896874264286

## Gate (unchanged)

Close #390 only when dumpsys shows:

- `versionCode=4`
- flags **without** `DEBUGGABLE`
- `installerPackageName=com.android.vending`

App Dist / debug APK / CI upload alone ≠ Play honesty.
