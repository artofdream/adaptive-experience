# Returning-shopper walk — 17 Aug 2026

tags: #aea #customer-journey
status: assessment-only
wait_tag: none
walked_url: https://localhost:8443/
payment_included: yes (session payment reference; no PAN)
walked_at: 2026-08-17T06:49+ Europe/Paris
assessed_by: aea-customer-journey
stack: Path A Edge Compose with inventory seeder. Did not open `/florist`. Did not invent a warehouse seeder or Anthropic key. Compose is **not** NFR-007 / NFR-012 proof.

## Scope

M8 returning-shopper path from `implementations/florist/journeys/returning-shopper-journey.md`: first mother-birthday order, then recall → reorder. Walker: `scripts/walk_returning_shopper.py --payment`.

Durable cross-session recall is #193 (do not implement here). Same-session T-03 hint is #190 (already on the shop).

## Outcome

**Path A full path works through same-session reorder.** After Create order, T-03 showed `Ordered earlier in this session` on Budget Mixed Bunch. Selecting that card and confirming destination `home` succeeded. A new browser (no cookies) did **not** offer a prior order — **blocked** until #193, not a product fail.

Path B (`https://aea.artof.link/`) was not re-walked this pass. Last-seen T-03 Select is disabled with `Unknown` availability. The walker **xfails / skips** Select on Path B in that case. Do not invent a seeder.

## Tile results

| Step | Tile | Result | Notes |
|------|------|--------|-------|
| 1 | T-01 Enter | pass | Welcome + free-text composer. No login. |
| 2 | T-01 thought completion | pass | Chips: for Mom, for a birthday, under $75. Typing remained available. |
| 3 | T-01 Send + T-02 | pass | birthday / mother / 75. Review and correct visible. No `csrf_rejected`. |
| 4 | T-03 | pass | Two Available cards under $75. Select enabled (Compose seeder). |
| 5 | T-04 | pass | Budget Mixed Bunch; size Standard; card message. |
| 6 | T-05 | pass | 2026-08-24 morning; destination `home`; no street-address fields. |
| 7 | T-06 | pass | Itemized total $47.00. |
| 8 | T-07 | pass | Session payment reference; ack; Create order 202 `submitted`. No PAN. |
| 9 | M8 same-session recall | pass | Hint on Budget Mixed Bunch after accepted order. |
| 10 | M8 reorder | pass | Selected hinted SKU; confirmed destination reference. |
| 11 | ASO Help | pass | Labeled not a person. Answer used session delivery facts. |
| 12 | M8 durable recall | blocked | New browser has no prior order. Waits on #193. |

## Blockers vs friction

- **Blocker for the M8 durable path:** no login-less recall after cookies are gone. Expected until #193. Same-session reorder is already walkable.
- **Friction:** none that stopped the Path A shopper. Journey chrome `Continue to recommendations` is hidden on later steps; the step rail still returns to T-03.
- **Path B:** skip/xfail Select when availability is unknown. Not a missing control.
- **Not this walk:** `/florist` not opened. `csrf_rejected` not seen. No Anthropic key. No seeder invented.

## How to run

```bash
docker compose -f edge/docker-compose.yml up --build --wait
python scripts/test_walk_returning_shopper.py
python scripts/walk_returning_shopper.py --payment
```

Path B (honest Select xfail):

```bash
python scripts/walk_returning_shopper.py --url https://aea.artof.link/ --skip-payment
```

## Evidence

- JSON: `research/assessments/2026-08-17-returning-shopper-walk.json`
- Walker: `scripts/walk_returning_shopper.py`
- Journey script: `implementations/florist/journeys/returning-shopper-journey.md`

## Highest-severity next step

#193 durable prior-order recall (no login). This script is ready to observe it when that slice lands. Do not treat this assessment as closing #27 / FR-008.
