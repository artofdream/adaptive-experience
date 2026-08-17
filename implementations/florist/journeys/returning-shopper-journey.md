# Journey: Returning shopper (recall → reorder)

M8 sample for FR-008 / US-008. Not an MVP first-time path. Does **not**
implement recall. Durable cross-session recall is #193. Same-session T-03
hint (#190) is already on the shop after an accepted order.

Payment / T-07 is optional. Same-session hint needs an accepted order, so a
walk that wants to observe that hint includes T-07 via the **session payment
reference** (no card number). Default mother-birthday walks still skip pay.

## Surfaces

| Path | URL | Full Select → customize → delivery |
|---|---|---|
| **A (Compose)** | `https://localhost:8443/` | Yes — local inventory seeder. This is the full script. Not NFR-007 / NFR-012 proof. |
| **B (pilot)** | `https://aea.artof.link/` | T-03 Select last-seen **disabled** (`Unknown` availability). Skip/xfail Select and every later tile. Do not invent a warehouse seeder or Anthropic key. |

Do not open `/florist` in the same browser as the shop.

## Script

1. Arrive as a customer. No login. Notice welcome and conversation (T-01).
2. First order uses the mother-birthday thought: `I need flowers...` then
   `Birthday flowers for Mum, under $75` (or the live thought-completion chip).
3. Review Shared Understanding (T-02). Correct if needed. Continue to
   recommendations.
4. T-03: pick an **Available** arrangement.
   - Path A: Select must be enabled.
   - Path B: if every Select is disabled and badges are `Unknown`, **xfail /
     skip** Select. Stop the first-order path there. That is fail-closed
     production inventory, not a missing journey control.
5. T-04: size, short physical card message, optional colour/ribbon.
6. T-05: date, named window, **confirm saved destination reference** (for
   example `home`). Do not type a street address (ADR-013).
7. T-06: summary itemizes charges.
8. T-07 (optional): confirm session payment reference, ack, Create order. No
   PAN fields. Skip unless the walk includes payment.
9. **Recall (same session):** after an accepted order, return to T-03. Expect
   `Ordered earlier in this session` on the prior SKU. Select it to reorder.
   Confirm the destination reference again — do not silent auto-apply.
10. **Recall (durable, no login):** new browser / cleared cookies. Expect the
    last accepted product (and destination reference) to be offered for
    reorder without an account. Until #193 this step is **blocked**, not a
    product fail.
11. Modify-before-reorder (M8 slice 4) is out of scope for this script until
    that slice exists.
12. Help (`?`) once — automated answers, not a person.

## How to run the walker

Path A (full path, Compose already up):

```bash
docker compose -f edge/docker-compose.yml up --build --wait
python scripts/walk_returning_shopper.py --payment
```

Path B (honest skip/xfail on Select):

```bash
python scripts/walk_returning_shopper.py --url https://aea.artof.link/ --skip-payment
```

`--skip-payment` is the default. `--payment` is required to observe the
same-session hint. Playwright: `pip install playwright` then
`playwright install chromium` (the walker also tries the Edge/Chrome channel).
