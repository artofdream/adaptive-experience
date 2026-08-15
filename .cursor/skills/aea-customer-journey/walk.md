# Customer walk — expected vs how to operate

Operate as a first-time shopper on `https://localhost:8443`. Expected column
comes from `mother-birthday-journey.md` and
`docs/03-functional-design/customer-journey.md`.

Payment/T-07 default: **excluded**. Mark those rows `blocked` (scope), not
`fail`.

## Step table template

Use this structure in the assessment canvas (not as a chat markdown table when
the canvas is the deliverable).

| Step | Tile | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | T-01 | Enter / Discovery: can describe the occasion in own words | | pass/fail/blocked |
| 2 | T-01, T-02 | Partial thought; suggestions optional; Shared Understanding updates; can review/correct | | |
| 3 | T-03 | Curated recommendations appear after intent; available options selectable | | |
| 4 | T-04 | Select arrangement; size; physical card message; optional flower/colour/ribbon | | |
| 5 | T-05, T-06 | Delivery date/window; confirm destination **reference**; summary itemizes charges | | |
| 6 | T-06, T-07 | Review and pay — **skip unless asked** | | blocked (scope) or walk |
| 7 | T-08 | Tracking after confirmed order — usually skipped with payment | | blocked (scope) or walk |
| — | ASO | Help available without leaving the workspace; labeled as not a person | | |

## How to walk each surface

### T-01 Conversation

- Landing: welcome + composer. Type in **Your message**.
- Mother-birthday: start with `I need flowers...` or the Birthday chip
  (`Birthday flowers for Mum, under €75`).
- Send. Wait for the log to show your message and an assistant reply.
- Chips are optional. If the only way forward is a chip, that is **friction**
  (thought-before-form expects free typing).

### T-02 Intent summary

- Occasion, recipient, budget, style, flower preference, timing should appear
  as you go.
- **Review and correct** should exist. Try one correction if the summary is
  wrong (e.g. recipient). Silent wrong intent with no way to fix is a **fail**.

### T-03 Recommendations

- Continue to recommendations (or journey step 3) after intent exists.
- Expect cards with availability. Prefer a card that looks available.
- Empty state asking for occasion/budget first is OK if you skipped intent.
- Recommendations are ranked options, not a chat inventing products.

### T-04 Customize

- After Select, set size and a short **card message** (physical card with the
  flowers — not a gift card).
- Thin options (flower type, colour, ribbon) may be present. Do not hunt for
  a bouquet builder.

### T-05 Delivery + T-06 Summary

- Date and a window (e.g. 10:00–12:00).
- **Confirm saved destination** (reference such as `home`). Do not enter a
  street address. A raw-address form is a **fail** against privacy, not a
  missing feature to add.
- Confirm delivery details. Order summary should show itemized charges.

### T-07 Checkout (optional)

Only if the user asked to include payment:

- Confirm destination, total, and session payment **reference**.
- Check the confirmation ack. Place Order. No card number fields.
- If the UI demands a card number, that is a **fail** (do not fill PAN).

Otherwise mark step 6 **blocked (payment not included)**.

### T-08 Tracking

Only after a confirmed order. Chat with Lily = automated Help. Contact
Florist = ask a person to follow up. Do not treat them as the same control.

### ASO Help

Open Help or `?` once. Expect automated answers from approved shop
information. Closing and continuing the order must remain possible.

## Blockers vs friction

**Blocker** — cannot continue the shopper path (Send does nothing, CSRF
reject, recommendations never appear, delivery will not confirm, workspace
did not boot).

**Friction** — continued, but it was confusing, slow, easy to miss, or
worded like a person when it is automated.

## CSRF observation

If Send or Confirm Delivery shows
`This session could not verify the request. Refresh the page, then try again.`
(`csrf_rejected`):

- Note whether `/florist` was opened in this browser (should not be, unless
  the user named it).
- Record as blocker; mention possible `!165` regression.
- Do not change BFF/cookie code unless the user asked this skill to fix it.

## Environment notes

- URL: `https://localhost:8443` — ephemeral self-signed cert.
- Inventory seeder runs with edge Compose so T-03 Select can succeed locally.
  Unknown/disabled Select on every card after a healthy boot may be a **fail**
  (availability), not a reason to edit seeders during an assessment-only run.
