# Session memory — #381 ROG back with cts-ai (2026-09-03)

> **Captured**: 2026-09-03
> **Owner**: `@aea-senior-software-engineer` with `@aea-customer-journey`
> **Tags**: #aea #companion #rog #t09 #t05 #381
>
> **Live brief**: [[2026-09-03]] (`research/daily-briefs/2026-09-03.md`)
> **Prior hold**: [[2026-09-03-session-memory-log-collab-bus]]

cts-ai is **back online with the ROG**. ADB lists `K9AIKN07B088C89` `ASUS_I001DC`. Grok-bot no longer holds this ADB lane for tonight.

## Claim

- Issue [#381](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/381) note: cts-ai taking companion T-09 + real T-05.
- Branch: `feat/381-companion-t09-real-t05` from `origin/main`.
- Do **not** restyle florist.js / shop CSS. #382 destination handle stays parked.

## Product change (companion only)

1. **T-05** — Pay chips for today/tomorrow, morning/afternoon/evening, `home`/`work` opaque refs. Checkout POSTs the chosen window and destination instead of hardcoded `today` + `afternoon` + `home`.
2. **T-09** — `POST /api/v1/support/escalation` with allowlisted `reason` only. Contact Florist in the top bar, Pay, and Track.

## Prove still required on ROG (after CI APK)

Host JDK is Temurin **17**; `compileSdk 36` needs **21**. Local `gradlew` failed `invalid source release: 21`. Use CI `android-build-debug` APK, then:

1. Sideload debug APK to ROG.
2. Need → Pick → Pay: choose **morning** + **work** (not the old defaults) → Confirm.
3. Order UUID on https://aea.artof.link/florist Staff orders, `channel=companion-android` (separate browser).
4. Contact Florist → T-09 row on `/florist` inbox.
5. Comment the order UUID on #381.

A36 stays the sponsor daily phone, not this probe.
