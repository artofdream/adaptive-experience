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
| Installs from Play | Play internal testing — not Firebase App Distribution or debug APK alone |
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

ASUS smoke (2026-09-02) re-check showed `DEBUGGABLE` + `installer=null` for versionCode 3 after Need→Pay. Release `buildTypes` now set `isDebuggable = false` explicitly. **Do not claim Play honesty for UX findings until the dedicated ASUS shows Play-signed non-debuggable with installer=`com.android.vending`.** Debug/FAD builds share `applicationId` with release for Firebase client match — sideload can overwrite Play installs.

