# Companion — thin native client

The Android companion is a **thin live-BFF client** for the Path B Need → Pick → Pay slice. It is not a port of the full Adaptive Workspace, not a second shop backend, and not a production Play Store claim.

Live BFF: [https://aea.artof.link](https://aea.artof.link) (same Edge contracts as the web shop). This framework page explains the architecture stance; the florist shop stays on that hostname.

## What “thin” means

- **Shared Understanding + Domain Services** still decide. The app posts conversation, selection, delivery, order, and checkout to the Edge BFF (cookie session + CSRF). It does not invent prices or inventory.
- **Need → Pick → Pay** is in scope. Full workspace tiles, SSE topic bus, and dual-viewport layout are **out** of the companion MVP.
- Catalog may use a local fallback list when recommendations are unavailable; selection and checkout still go to the BFF. Sold-out stays fail-closed.
- Checkout sends an opaque payment reference only — no raw card fields.

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
| Native vs web traffic in Grafana | Requires an explicit client channel label on requests — not a separate auth token for MVP |

## Related on this site

- [Path B case study](path-b.html) — live florist workspace and journey tapes
- [Stack](stack.html) — hostnames and runtime shape
- [Glossary](glossary.html) — Path B and status words
- [Framework home](index.html)

Status words need a probe. AI may interpret; domain services decide.
