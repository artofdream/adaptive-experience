# Companion Anniversary card prefill (#389)

> **Tags**: #aea #companion #ux #gap-loop #honesty
> **Captured**: 2026-09-02
> **Issue**: [#389](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/389)
> **MR**: !408
> **Related**: [[2026-09-02-asus-play-v3-smoke-native-gaps]] · [[2026-09-02-companion-native-web-gap-closing-loop]] · [[2026-09-02-florist-operator-native-web-completeness-gaps]]

## Live evidence

Anniversary path (`Anniversary ($80)` chip) prefills enclosure **Happy Birthday Mom! Love always.** on Pay (`06-pay.png`).

## Fix

`SessionRepository.defaultCardMessage(occasion, recipient)` + `PayScreen` remember keys. Anniversary → anniversary copy; unknown → empty. Unit test asserts no Birthday/Mom on anniversary.

## Honesty

Paparazzi Pay snapshot may need re-record. Does not claim Play honesty (#390).

