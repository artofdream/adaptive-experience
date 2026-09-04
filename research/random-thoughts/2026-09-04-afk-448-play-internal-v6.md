# AFK: !448 companion Pick/Pay photos + Play Internal v6

> **Tags**: #aea #vault #afk #companion #play-internal #mrc
> **Date**: 2026-09-04
> **Canonical path**: `research/random-thoughts/2026-09-04-afk-448-play-internal-v6.md`
> **Why not daily-brief**: `research/daily-briefs/2026-09-04.md` already exists on main (generated governance brief); this AFK capture is a separate probe-backed note to avoid overwrite/conflict risk.

## Plain

Today MR !448 landed on main: the companion app now maps Pick/Pay product photos through Coil + CatalogArt to CDN assets at `https://aea.artof.link/assets/sku-*.jpg`, shipped as versionCode 6 / versionName 0.1.0-alpha.6. After merge the first main pipeline stalled on `ci_quota_exceeded` (jobs never started); once the sponsor bought compute minutes and pipeline 2820784659 was retried, release bundle, Play Internal upload (completed for `link.artof.aea.companion` v6), and Firebase App Distribution all succeeded — no cts-ai work was needed for that CI/Play path. Draft !434 remains hold/undrafted. Device prove of Pick photos / dumpsys honesty for v6 is **UNKNOWN** at note-write time (not claimed phone-proved).

## Vault

- **!448 MRC** — `feat(companion): product photos on Pick/Pay (#397)` merged to main.
  - Mechanism: Coil + CatalogArt mapping → `https://aea.artof.link/assets/sku-*.jpg`
  - App version: **versionCode 6** / **versionName 0.1.0-alpha.6**
  - Merge commit: `34be0564fc60` (`34be0564fc60e8ac2ff6e7ecb816b70f6e5d344a`)
  - Issue **#397** closed via `Closes` trailer
- **Main pipeline post-merge**
  - First run failed with `failure_reason: ci_quota_exceeded` (jobs never started; empty traces)
  - Sponsor bought compute minutes; **retry of pipeline 2820784659** then ran and reached `success` on `main` @ `34be0564fc60…`
- **After retry (probe-backed)**
  - `android-bundle-release` — success
  - `android-play-internal-upload` — success — package `link.artof.aea.companion` **versionCode 6**, track **internal**, status **completed** (job `16311744258`)
  - `android-app-distribution` — success (debug APK to Firebase App Distribution)
- **Device prove (Pick photos / dumpsys honesty for v6)**: **UNKNOWN** at note-write time — do **not** claim phone proved unless separately confirmed.
- **Draft !434**: still **draft / hold / undrafted** (`Draft: feat(operator): parallelize boot, add pagination, bounded retry for operator efficiency`).
- **cts-ai**: no activity required for the CI / Play Internal path above.
