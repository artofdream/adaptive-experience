# Native↔web gap-closing — technical handoff (2026-09-02)

> **Tags**: #aea #florist #companion #gap-loop #honesty #fr-013 #knowledge-first #mrc
> **Captured**: 2026-09-02 evening Europe/Berlin (UTC+2)
> **Audience**: agents / MRC / implementers
> **Plain twin**: [[2026-09-02-native-web-florist-story-plain-language]]
> **Wikilinks (verified on main)**: [[2026-09-02-florist-operator-native-web-completeness-gaps]] · [[2026-09-02-asus-play-v3-smoke-native-gaps]] · [[2026-09-02-companion-native-web-gap-closing-loop]]
> **Public**: [architecture.artof.link/companion](https://architecture.artof.link/companion)

## Sponsor goals (this loop)

| Goal | Status tonight |
|------|----------------|
| **(A)** Close native↔web gaps | Write-through **PASS** both channels; field completeness partially merged; channel live status **Unknown**; companion UX MRs open |
| **(B)** Document knowledge in two tracks | This note (technical) + [[2026-09-02-native-web-florist-story-plain-language]] (humans) |

## Dual-probe order_ids (live Path B)

| Channel | order_id | Checkout (UTC) | Staff list |
|---------|----------|----------------|------------|
| Web | `cd662171-785b-4400-af33-ea9be33aec8b` | 2026-09-02 **19:53:11Z** | HIT |
| Native Play (fresh Confirm) | `b2eedd00-c2ea-44af-a4b2-bbc1ff4384e6` | 2026-09-02 **19:54:44Z** | HIT |
| Native (prior same day) | `309078ad-e50c-433e-880b-e31312ded612` | earlier | still on list |

Web checkout corr (report): `b7919a10-8195-40e8-bd76-b805a31527b9`.

**Do not residual-claim #360.** Write-through evidenced; remaining work is field completeness + companion UX + Play honesty.

## Evidence paths

| Path | Contents |
|------|----------|
| Box `/workspace/aea-florist-dual/` | `FLORIST-DUAL-REPORT.md`, `operator-orders*.json`, `native-*-session.json`, checkout evidence |
| Host `C:\Users\claud\AppData\Local\Temp\aea-florist-dual\` | Dual-probe screenshots / session dumps |
| Box `/workspace/aea-play-v3-smoke/` | ASUS Need→Pick→Pay smoke screenshots |
| Host `C:\Users\claud\AppData\Local\Temp\aea-play-v3-smoke\` | Same smoke evidence |
| Vault | [[2026-09-02-florist-operator-native-web-completeness-gaps]] · [[2026-09-02-asus-play-v3-smoke-native-gaps]] · [[2026-09-02-florist-operator-session-facts-383-385]] |

## Issue → MR map

| Issue | Topic | MR(s) | Issue state | Notes |
|-------|-------|-------|-------------|-------|
| **#383** | Staff list/detail hide `card_message` | **!409** (list columns) · **!418** (session facts) | **closed** | !418 `Closes #383` (merged 2026-09-02T20:47Z) |
| **#384** | Operator orders lack web vs companion channel (`aea_client`) | **!409** (persist allowlisted client / migration 023) · **!418** (session facts `Related #384`) | **opened** | Live channel badge = **Unknown** until redeploy + re-probe; do not close from docs |
| **#385** | Product title / paid total missing | **!409** · **!418** | **closed** | !418 `Closes #385` |
| **#387** | Budget soft-filter still lists under-band SKU | **!410** (open) · also bundled **!416** | opened | Inclusive band / hide under-floor |
| **#388** | Budget chip collapses to `100.0` | **!414** (open) · **!416** | opened | Preserve chip label through Pick/Pay |
| **#389** | Anniversary prefills Birthday Mom card | **!408** (open) · **!416** | opened | Occasion-aware Pay card default |
| **#390** | ASUS v3 `DEBUGGABLE` + `installer=null` | **!419** (open docs) | opened | Honesty gate — not florist UI |

Related already-shipped context (do not rediscover): !401 staff list (#360), !388/`#368` `X-AEA-Client` Grafana-only, !376/!379/!380 thin BFF companion. Prefer parent ids over dups #375/#377.

### Merge order preference

1. **Florist operator readability** — !409 (merged) → !418 (merged). Redeploy florist UI before claiming live card/title/total/channel.
2. **Companion UX (#387→#388→#389)** — prefer landing !410, !414, !408 (or single !416 if MRC chooses the bundle) before re-smoke on ASUS.
3. **#384 live verify** — after florist redeploy, confirm channel on operator orders + `_operator_summary` + `/florist` badge for web `cd662171-…` and native `b2eedd00-…` (new orders may be needed if pre-migration rows stay empty).
4. **#390 Play honesty** — land docs/release notes (!419); prove Play-signed **non-DEBUGGABLE** with `installer=com.android.vending` before any “from Play Store” claim.

## Honesty gates (do not soften)

| Gate | Rule |
|------|------|
| **FR-013 least-data** | Card text, catalog title, paid total, allowlisted channel = fulfillment fields. No email/raw street PII / CRM expansion. |
| **Sample ≠ live** | `SAMPLE_ORDERS` / `SAMPLE_INBOX` ≠ live CRM. Tonight’s dual-probe used live operator APIs (HTTP 200). |
| **Play ≠ DEBUGGABLE** | App Dist / debug APK ≠ Play internal honesty. `DEBUGGABLE` + `installer=null` ≠ “installed from Play” even if versionCode matches. |
| **Merged ≠ live** | !418/!409 closed code gaps for #383/#385; live florist screen needs redeploy + look-again. |
| **#384** | Related by !418; **not** closed. Status Unknown/check live. |
| **T-09** | Contact Florist dual-probe not run tonight — leave Unknown. |

## Remaining open after this knowledge MR

- **#384** — channel on live `/florist` (persist may exist post-!409; prove on new orders).
- **#390** — Play honesty on dedicated ASUS.
- **#387 / #388 / #389** — companion UX MRs still open at capture time.
- Redeploy + dual re-check (phone + florist) after merges.

## Agent rules

- Knowledge-first: read the three verified vault notes above + this handoff before opening new parity issues.
- One finding → one issue → one MR; link back to [[2026-09-02-companion-native-web-gap-closing-loop]].
- This docs MR **Closes none**.
- Do not invent wikilink slugs; the three related notes were verified present on `main` before this MR.
