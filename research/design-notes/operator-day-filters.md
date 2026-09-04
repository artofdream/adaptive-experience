# Design note — Operator per-section day filters (#398)

status: proposed (2026-09-04)
for_issues: "#398 (operator day filters, applicable by section)"
affects: "local Edge operator console /florist (client-side only): Staff orders + Contact Florist inbox filter groups"
author: cursor
date: 2026-09-04

> **Decisions (2026-09-04):**
> 1. Day windows are **per section**, not a single global control. Each dated
>    triage list owns its own filter group so an operator can scope Staff
>    orders and the Contact Florist inbox independently.
> 2. The windows are **directional**, matching what each list means:
>    - **Staff orders → upcoming.** An order is in the `3 days` / `7 days`
>      window when its **delivery date** (`timing.date`) is between today and
>      today+N inclusive. This answers "what must I prepare next." `updated_at`
>      is deliberately **not** used for the forward window — it is a past
>      timestamp, so a far-future or delayed order touched recently would
>      otherwise leak into a "next N days" list (caught by the logic test
>      before merge).
>    - **Contact Florist inbox → recent.** A request is in the window when its
>      `requested_at` is between today and today−N inclusive (requests are
>      always in the past).
> 3. `Today` keeps the existing order semantics (`isTodayOrder`: delivered
>    today OR updated today) so the derived **Prepare** list is unchanged.
>    `3 days` / `7 days` are purely additive delivery-horizon windows.
> 4. Client-side only. No API/shape change; this filters already-fetched
>    least-data reads (NFR-017 unaffected). Prepare stays today-scoped by
>    design; Forecast is trend-based, so neither gets a day filter.

## Grounding

- Builds directly on the operator surface in `florist-operator-ui.md` (#170)
  and AGY's responsive pass (#382). This branch is cut from current `main`.
- Reuses the existing `.operator-filter-wrap` / `.operator-filter-btn` pill
  pattern and `aria-pressed` state already shipped for the orders
  Today/Delayed/All group — no new CSS.

## Behaviour

| Section | Control ids | Windows | Field | Direction |
|---|---|---|---|---|
| Staff orders | `order-filter-{today,3d,7d,delayed,all}` | Today · 3 days · 7 days · Delayed · All | `timing.date` | upcoming (0..+N) |
| Contact Florist inbox | `inbox-filter-{today,3d,7d,all}` | Today · 3 days · 7 days · All | `requested_at` | recent (−N..0) |

- State: `state.orderFilter` (default `today`), `state.inboxFilter` (default
  `all` — the inbox is small and triage-critical, so nothing is hidden by
  default). The two are independent; changing one never re-renders the other's
  data set.
- The inbox keeps the **full** fetched set in `state.items` (so the
  cross-section "Has order" badge on Staff orders still resolves) and renders
  only the filtered subset.
- Range-aware empty copy: "No orders in the next 3/7 days.", "No delayed
  orders.", "No orders for today.", and "No Contact Florist requests in this
  day range."

## Helpers (florist.js)

- `dayDiffFromToday(value)` — signed local-calendar day delta. Parses both a
  `YYYY-MM-DD` delivery date and an ISO datetime as a **local** date, so the
  window is timezone-stable and consistent with `isTodayOrder`'s string match
  (avoids a UTC off-by-one).
- `orderWithinDays(item, n)` — `0 <= dayDiff(timing.date) <= n`.
- `inboxWithinDays(item, n)` — `-n <= dayDiff(requested_at) <= 0`.

## Verification

- `edge/tests/test_browser_ui.py` asserts the new controls, helpers, and
  defaults.
- A standalone Node harness extracts the real pure helpers from `florist.js`
  and asserts the partition against synthetic rows at today / +2 / +5 / +10 /
  +30(delayed) and inbox at −0 / −2 / −5 / −10. This is what caught the
  `updated_at` forward-leak; it is a scratch check, not committed.
- Live-verified on the running gateway with seeded dated orders across
  laptop / tablet / phone.

## Out of scope

- Custom date-range pickers, saved filter presets, and per-window counts on
  the pills (possible follow-ups; see the UX assessment on #398).
- Any server-side filtering or new endpoints.
