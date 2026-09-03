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
| Installs from Play | **Probed 3 Sep 2026 (#390):** Play Internal versionCode **4**, flags without `DEBUGGABLE`, installer=`com.android.vending` (clean install after removing adb sideload). Debug/FAD alone is still not Play |
| Florist staff list shows web vs companion channel | **Probed 3 Sep 2026 (#384):** Path B migration 023 (`aea_client`); fresh web checkout with `X-AEA-Client: web` showed `channel=web` on `/florist` operator orders |
| Website / atelier write-through after Confirm | Sponsor dual-probe (companion Confirm → website tracking) — still open |
| Operator inbox = live orders | **No.** Sample operator surfaces are not the billing CRM |
| Native vs web traffic in Grafana | **Query documented / panel as-code (#368):** clients send `X-AEA-Client` (`companion-android` / `web`); BFF/edge log `aea_client`. As-code panels on uid `aea-unified-dashboard` (`BFF requests by aea_client`, status table). Logs Insights + verify steps: vault `research/random-thoughts/2026-09-02-x-aea-client-grafana-label.md`. Live series need edge/BFF+Grafana redeploy + traffic probe |

## Related on this site

- [Path B case study](path-b.html) — live florist workspace and journey tapes
- [Stack](stack.html) — hostnames and runtime shape
- [Glossary](glossary.html) — Path B and status words
- [Framework home](index.html)

Status words need a probe. AI may interpret; domain services decide.

## Play honesty gate (#390)

ASUS smoke (2026-09-02) first showed `DEBUGGABLE` + `installer=null` for versionCode 3 after Need→Pay (adb/FAD sideload). Release `buildTypes` keep `isDebuggable = false`. **Probed 3 September 2026:** after uninstalling the sideload and installing Play Internal versionCode **4**, dumpsys showed flags without `DEBUGGABLE` and `installerPackageName=com.android.vending`. Sideload can still overwrite a Play install when `applicationId` matches — use Play for honesty claims.

## Florist channel on staff orders (#384)

Web and companion checkouts both write through to the live florist staff list. Operators need a **channel** label (`web` / `companion-android`). That field is persisted as allowlisted `aea_client` (migration 023) and returned on operator orders. **Probed 3 September 2026** on Path B: after applying the migration, a fresh web checkout with `X-AEA-Client: web` showed `channel=web` on `/florist`. Pre-migration rows may still show a null channel.

