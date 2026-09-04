# Companion — thin native client

The Android companion is a **thin live-BFF client** for the Path B Need → Pick → Pay slice. It is not a port of the full Adaptive Workspace, not a second shop backend, and not a production Play Store claim.

Live BFF: [https://aea.artof.link](https://aea.artof.link) (same Edge contracts as the web shop). This framework page explains the architecture stance; the florist shop stays on that hostname.

## What “thin” means

- **Shared Understanding + Domain Services** still decide. The app posts conversation, selection, delivery, order, and checkout to the Edge BFF (cookie session + CSRF). It does not invent prices or inventory.
- **Need → Pick → Pay** is in scope. Full workspace tiles, SSE topic bus, and dual-viewport layout are **out** of the companion MVP.
- Catalog may use a local fallback list when recommendations are unavailable; selection and checkout still go to the BFF. Sold-out stays fail-closed.
- Checkout sends an opaque payment reference only — no raw card fields.

## Native Need tape (2 September 2026)

30-second phone recording of the live-BFF companion on Need. Tapping **Mom's Birthday (Same-Day)** unlocks **View Arrangements (birthday)**. This is that evening's Need-step evidence, not Confirm write-through, not Play, and not a dual-viewport shop clip.

![Companion Need, 2 September 2026, 30 seconds](assets/companion-need-30s-2026-09-02.mp4)

## Gap-closing loop

Native and web share contracts. Drift shows up as App Tester 409s (for example product-only totals vs delivery-inclusive `order_summary.total`, or Start Over reusing session cookies). The loop is honesty-first:

1. **Detect** — App Tester, contract tests, weekday API probe, Grafana client split.
2. **Decide** — one finding → one issue.
3. **Ship** — smallest companion or edge change.
4. **Prove** — automated regression where cheap; sponsor dual-probe where claims need human proof.

Unprobed claims stay **Unknown**.

## Honesty gates

| Claim | Gate |
|-------|------|
| Installs from Play | **Probed 4 Sep 2026 (#390):** Play Internal versionCode **5**, flags without `DEBUGGABLE`, installer=`com.android.vending` verified on ASUS ROG (`ASUS_I001DC`, `K9AIKN07B088C89`). Debug/FAD alone is still not Play |
| Florist staff list shows web vs companion channel | **Probed 3–4 Sep 2026 (#375, #384):** Live checkout from ASUS ROG (order `34091114-cb91-44de-a5a3-6be78c503912`) wrote through to ECS Fargate operator feed at `https://aea.artof.link/api/v1/operator/orders` with `client: companion-android` verified in production |
| Companion Contact Florist & choosable delivery | **Probed 4 Sep 2026 (#381):** Pay screen confirms choosable delivery window (morning/afternoon/evening) and destination ref; T-09 Contact Florist escalation lands in live operator inbox |
| Website / atelier write-through after Confirm | Sponsor dual-probe: order `34091114-cb91-44de-a5a3-6be78c503912` confirmed written to backend order aggregate |
| Operator inbox = live orders | **No.** Sample operator surfaces are not the billing CRM |
| Native vs web traffic in Grafana | **Query documented / panel as-code (#368):** clients send `X-AEA-Client` (`companion-android` / `web`); BFF/edge log `aea_client`. As-code panels on uid `aea-unified-dashboard` (`BFF requests by aea_client`, status table). Logs Insights + verify steps: vault `research/random-thoughts/2026-09-02-x-aea-client-grafana-label.md`. Live series need edge/BFF+Grafana redeploy + traffic probe |

## Related on this site

- [Path B case study](path-b.html) — live florist workspace and journey tapes
- [Stack](stack.html) — hostnames and runtime shape
- [Glossary](glossary.html) — Path B and status words
- [Framework home](index.html)

Status words need a probe. AI may interpret; domain services decide.

## Play honesty gate (#390)

ASUS smoke (2026-09-02) first showed `DEBUGGABLE` + `installer=null` for versionCode 3 after Need→Pay (adb/FAD sideload). Release `buildTypes` keep `isDebuggable = false`. **Probed 4 September 2026:** after release pipeline `#2818539184` on `main` deployed versionCode **5** to Google Play Internal Track, dumpsys on ASUS ROG (`ASUS_I001DC`) showed:
```text
versionCode=5 minSdk=26 targetSdk=36
installerPackageName=com.android.vending
pkgFlags=[ HAS_CODE ALLOW_CLEAR_USER_DATA ALLOW_BACKUP ]
```
Both test handsets (Samsung Galaxy A36 on v4 and ASUS ROG on v5) now have verified non-debuggable Play-signed release builds directly from the Google Play Store.

## Florist channel on staff orders (#375, #384)

Web and companion checkouts both write through to the live florist staff list. Operators need a **channel** label (`web` / `companion-android`). That field is persisted as allowlisted `aea_client` (migration 023) and returned on operator orders. **Probed 4 September 2026** on Path B: a real checkout from the ASUS ROG handset generated order `34091114-cb91-44de-a5a3-6be78c503912` ($82.00 total for `classic-rose-dozen`), which appeared live at the top of `GET https://aea.artof.link/api/v1/operator/orders` with `client: companion-android`. Issue #375 closed.

