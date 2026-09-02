# ASUS Play v3 smoke — native companion gaps

> **Tags**: #aea #companion #play #smoke #honesty #gap-loop #knowledge-first #asus
> **Captured**: 2026-09-02 evening Europe/Berlin (UTC+2)
> **Owners**: `@aea-knowledge-guardian` · `@aea-ux-designer` · `@aea-devsecops-platform` · sponsor AFK
> **Device**: dedicated **ASUS_I001DC** on cts-ai · Play internal opt-in URL · `versionCode` **3** / `0.1.0-alpha`
> **Evidence path**: `C:\Users\claud\AppData\Local\Temp\aea-play-v3-smoke\` (also box `/workspace/aea-play-v3-smoke/` screenshots)
> **Issues**: [#387](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/387) · [#388](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/388) · [#389](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/389) · [#390](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/390)
> **Related**: [[2026-09-02-florist-operator-native-web-completeness-gaps]] · [[2026-09-02-play-api-ci-upload-closed-testing]] · [[2026-09-02-native-client-validation-alternatives]] · [[2026-09-02-companion-native-web-gap-closing-loop]]

## Smoke slice

Need → budget → Pick → Pay (**Confirm skipped** for this UX gap capture). Screenshots: `01-launch.png`, `03-budget-selected.png`, `04-pick.png`, `06-pay.png`.

Separate florist dual-probe later the same evening confirmed a fresh native Confirm write-through (`b2eedd00-…`) — that is **not** this smoke’s claim; see the florist completeness note.

## Gaps → issues

| # | Finding | Evidence |
|---|---------|----------|
| **#387** | Budget soft-filter: chip **$50–100** still lists **Budget Mixed Bunch $35** on Pick | `03-budget-selected.png` → `04-pick.png` |
| **#388** | Budget band collapses to numeric **`100.0`** after product select (Pay / filter) | select → Pay screenshots |
| **#389** | **Anniversary** journey prefills enclosure card **Happy Birthday Mom! Love always.** | `06-pay.png` after Anniversary → budget → Classic Rose Dozen |
| **#390** | Install honesty: **`DEBUGGABLE`** + **`installer=null`** on versionCode 3 | `pm list packages -i` / dumpsys flags after smoke |

## Play honesty gate (#390)

Earlier the same day, dumpsys **briefly** showed `installerPackageName=com.android.vending` for versionCode 3. Re-check after Need→Pay smoke:

- `installer=null`
- package flags include **DEBUGGABLE**
- still `0.1.0-alpha` / versionCode 3

**Do not claim Play honesty** for UX findings (#387–#389) while the dedicated ASUS shows DEBUGGABLE and `installer=null`. Possible causes: debug/App Distribution overwrite after Play install, unexpected artifact on internal track, or device state drift — prove Play-signed non-debuggable with installer=`com.android.vending` before calling the smoke a Play gate.

## Observe-only

Price locale rendering as **`$70,00`** (comma decimal) noted as **observe-only** unless product decides locale policy. Not filed as a bug in this capture.

## Honesty (do not soften)

- App Distribution / debug APK ≠ Play internal honesty.
- DEBUGGABLE + `installer=null` ≠ “installed from Play” proof, even if versionCode matches the Play upload.
- This note does **not** close #387–#390 (knowledge capture only).
- Confirm / florist write-through is documented on [[2026-09-02-florist-operator-native-web-completeness-gaps]], not claimed from the Confirm-skipped smoke alone.
