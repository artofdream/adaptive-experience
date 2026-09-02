# Florist operator: native↔web completeness gaps

> **Tags**: #aea #florist #operator #completeness #companion #path-b #honesty #knowledge-first #fr-013
> **Captured**: 2026-09-02 evening Europe/Berlin (UTC+2)
> **Owners**: `@aea-knowledge-guardian` · `@aea-ux-designer` · `@aea-devsecops-platform` · sponsor AFK
> **Issues**: [#383](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/383) card · [#384](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/384) channel · [#385](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/385) title/total
> **Related**: [!401](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/401) staff order list · [#368](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/368) `X-AEA-Client` Grafana only (closed) · [#360](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/360) closed by !401 — write-through evidenced; **completeness** is the remaining story (#383/#384/#385)
> **Evidence**: live `https://aea.artof.link` · `C:\Users\claud\AppData\Local\Temp\aea-florist-dual\` · box `/workspace/aea-florist-dual/FLORIST-DUAL-REPORT.md`
> **Sibling**: [[2026-09-02-asus-play-v3-smoke-native-gaps]] · [[2026-09-02-companion-native-web-gap-closing-loop]]

## Florist-side goal

The operator must get the info they need to fulfill from **web and native** checkouts alike: card text, channel, product title, and paid total — without turning `/florist` into CRM (FR-013 least-data).

## Dual-probe write-through (DONE — 2026-09-02)

Live operator APIs **PASS** (HTTP 200 with session; **not** sample-only). Staff list shows both channels:

| Channel | order_id | checkout time (UTC) | on staff list |
|---------|----------|---------------------|---------------|
| Web | `cd662171-785b-4400-af33-ea9be33aec8b` | 2026-09-02 **19:53:11Z** | HIT |
| Native Play (fresh) | `b2eedd00-c2ea-44af-a4b2-bbc1ff4384e6` | 2026-09-02 **19:54:44Z** | HIT |
| Native (prior) | `309078ad-e50c-433e-880b-e31312ded612` | earlier same day | still on list |

**Do not re-open or residual-claim #360.** Write-through to the staff order list is evidenced for web and native. Remaining work is **field completeness** only (#383 / #384 / #385).

Fresh native shopper facts (same probe): Budget Mixed Bunch $35+$12=**$47**; card `Happy Birthday Mom! Love always.`; dest UI **LILY-PARIS-01** vs stored opaque **`home`** — OK (least-data; not street PII).

## Live API vs florist.js (completeness)

| Surface | Observation |
|---------|-------------|
| `GET /api/v1/operator/orders` | Returns `card_message` on least-data items when present |
| `florist.js` `renderOrders` | **Omits** card column; list shows SKU slug / status / timing |
| Session summary facts | Often **lacks** card on `selection` (product_id only); UI looks for `summary.selection.card_message` |
| Operator payloads | **No** `aea_client` / channel on orders or `_operator_summary` (#368 is Grafana/access-log only) |
| Order facet | id / status / delayed — **no** product title, unit price, delivery fee, or paid total |
| `florist.js` money UI | **Zero** total rendering |

Prefer parent issue ids: #375/#377 were opened earlier as dups of #384/#385.

## Field completeness table

| field | web→florist | native→florist | gap | issue |
|-------|-------------|----------------|-----|-------|
| order_id | `cd662171-…` | `b2eedd00-…` / `309078ad-…` | PASS write-through | — |
| status | submitted | submitted | PASS | — |
| product_id | classic-rose-dozen | budget-mixed-bunch | PASS slug only | — |
| product_display_name | MISSING | MISSING | FAIL florist lacks title | #385 |
| unit_price | MISSING | MISSING | FAIL | #385 |
| delivery_fee | MISSING | MISSING | FAIL | #385 |
| order_total | MISSING on operator order/session | MISSING | FAIL | #385 |
| card_message | PRESENT on list API (+ often session) | PRESENT on list API (+ session) | API PASS; **UI list hides card** | #383 |
| occasion | PRESENT session | PRESENT | PASS session pane | — |
| recipient | PRESENT session | PRESENT | PASS session pane | — |
| budget | often MISSING web intent | PRESENT native intent | PARTIAL | Unknown (not #383–385) |
| timing | PRESENT | PRESENT | PASS | — |
| destination_reference | home | home (UI may show LILY-PARIS-01) | opaque ref OK / least-data | — |
| channel / `aea_client` | MISSING | MISSING | FAIL | #384 |
| conversation transcript | PRESENT | PRESENT | PASS | — |
| Contact Florist / T-09 | live escalations API exists | same | **Unknown** — not dual-probed this turn | do not claim T-09 done |

## Issues (open — knowledge only; this MR does not close them)

1. **[#383](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/383)** — Staff list/detail hide `card_message` the atelier needs (API already has it).
2. **[#384](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/384)** — No web vs companion channel on operator payloads (`aea_client` Grafana-only today via #368).
3. **[#385](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/385)** — No product title / paid total in order facet; `florist.js` never renders total.

## Honesty (do not soften)

- **Sample inbox ≠ live CRM.** `SAMPLE_ORDERS` / `SAMPLE_INBOX` are boot fallbacks; this probe used live operator APIs (200). Still not billing CRM (#35/#36 parked).
- **Least-data FR-013** — no email/raw PII. Card text, title, total, and channel are operational fulfillment fields, not a CRM expansion.
- **#360 is closed** (!401). Do **not** claim a #360 residual. Completeness = #383/#384/#385.
- **T-09 / Contact Florist dual-probe = Unknown** (not run this turn). Live escalations history ≠ unpaid T-09 work done.
- Destination UI label vs stored opaque `home` is expected least-data behavior.

## What NOT to automate from this note

- Auto-closing #383/#384/#385 from knowledge MRs.
- Treating sample florist rows as an orders oracle.
- Using `X-AEA-Client` / channel badge as an auth boundary.
- Claiming T-09 dual-probe from this capture.
