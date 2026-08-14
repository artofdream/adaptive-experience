# Design note — M6 order tracking (#42, FR-023)

status: accepted (2026-08-13)
for_issues: "#42 (FR-023 Order Tracking, T-08)"
affects: "M6; builds on #32 order aggregate, #34 status lifecycle, #38 confirmation"
author: claude
date: 2026-08-13

> **Decisions (2026-08-13):**
> 1. Status vocabulary: add `completed` (terminal, after `delivered`) to the linear
>    sequence. Model `delay` as an orthogonal boolean flag (`delayed`), not a
>    linear status, so the forward-only advance rule (#34) is preserved; the
>    published/displayed authoritative state is `delayed` while the flag is set,
>    otherwise the linear status.
> 2. Display via the existing workspace `order` facet (poll/refetch). Reactive SSE
>    push of order-status changes is deferred to the M7 event backbone (#149),
>    where a running consumer reflects `order.status.updated` into the stream - it
>    does not belong half-built in #42.
> 3. "Contact Florist" (human contact) is FR-006/T-09 Future, not FR-023; out of
>    scope.

## Grounding

- FR-023: "publish order preparation, dispatch, delivery, **delay**, and
  **completion** status through a versioned order-status topic and **display the
  latest authoritative state** to the customer." Latest state, not a full history.
- `order.status.updated` (order -> orchestration/workspace, `{order_id,
  authoritative_status}`) exists (#34). The workspace `order` facet already
  displays the current status (#32/#34).
- Current statuses (mig-009): `created, submitted, confirmed, preparing,
  dispatched, delivered` (+ `cancelled`).

## Model (#42)

- **Migration 010:** add `completed` to the status CHECK; add `delayed boolean
  NOT NULL DEFAULT false`.
- **order.py:** `ORDER_STATUS_SEQUENCE` gains `completed`
  (`... delivered -> completed`); `advance_status` continues forward-only. Add a
  `set_delay(session_id, delayed)` order/fulfillment authority action that toggles
  the flag and publishes `order.status.updated` with `authoritative_status`
  = `delayed` (set) or the current linear status (cleared).
- **Authoritative state** surfaced to the customer =
  `delayed` if the flag is set, else the linear `status`.
- **Workspace `order` facet** exposes `{order_id, status, delayed,
  authoritative_status}`; the edge shapes it least-data.
- **Internal routes:** reuse `POST .../order/status` (advance, incl. `completed`);
  add `POST .../order/delay` (set/clear the flag). Both are authoritative
  (order/fulfillment), not customer actions - the customer reads via the facet.

## Not changing

- No status-history table (FR-023 is latest-state). No new browser route (tracking
  is the workspace facet). No reactive push here (M7 / #149).

## Build order within M6

`#42 (tracking)` then `#28 (FR-009 automated FAQ)` and `#24 (FR-005 approved
answers)` as synchronous read/response projections (mirroring conversation /
recommendations), so M6 adds no dependency on the not-yet-running bus (#149).
