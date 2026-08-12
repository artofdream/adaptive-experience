# Design note — Edge workspace projection + stream contract (#144)

status: accepted (Option A, 2026-08-12)
for_issue: "#144 (M4 reactive edge substrate)"
affects: "#142 (M3 recommendations/selection), CF-037 (verified)"
author: claude
date: 2026-08-12

> **Decision:** Option A endorsed 2026-08-12 - single aggregate workspace
> projection with tiles as namespaced facets and a `changed_facets` SSE stream;
> thin fallback only for write echoes. #142 read surface updated to consume
> workspace facets (no standalone `GET /api/v1/recommendations`).

## Decision to settle before code

Issue #144 introduces the aggregate **workspace projection** and the **SSE
stream**. Issue #142 (built right after) adds recommendations and selection. We
must decide up front how per-tile state (recommendations, selection, delivery,
...) is exposed, or #142 will diverge from #144 and force rework.

## Grounding (current code)

- Experience state is a namespaced facet document. Patches carry
  `changed_facets`, e.g. `shared_understanding.occasion`,
  `thought_completion.suggestions` (`platform/aea_platform/state.py`,
  `intent.py:279`). This is already the invalidation signal.
- Internal API routes `sessions/{id}/conversation` and
  `sessions/{id}/shared-understanding` only (`platform/aea_platform/internal_api.py`).
- The BFF already exposes `GET /api/v1/workspace` and `GET /api/v1/stream` and
  applies least-data shaping (`edge/bff/aea_bff/app.py:183,187`), but
  `HttpOrchestration.workspace_projection`, `stream_events`, and `accept_command`
  are stubs returning `orchestration_unavailable`
  (`edge/bff/aea_bff/orchestration.py:85-93`). CF-037 documented this.
- SSE wire format is set: `id: <event_id>` / `event: workspace` / `data: <json>`,
  resumable via `Last-Event-ID` or `?after=`.

## Options

- **A - Single aggregate projection, tiles are facets.** `/api/v1/workspace`
  returns the whole least-data facet document; each tile (conversation,
  shared_understanding, recommendations, selection, delivery, ...) is a namespaced
  branch. #142 recommendations/selection become facets, not new routes.
- **B - Standalone per-tile routes.** Each tile keeps its own GET
  (`/recommendations`, `/selection`, ...); no aggregate. Workspace is thin or
  omitted; stream just signals "something changed, refetch".
- **C - Hybrid.** Aggregate workspace projection for read/render, plus retained
  per-resource routes for write-heavy or independently paged tiles.

## Recommendation: A, with a thin C fallback

Adopt **A**. The state document is already a namespaced facet tree with a
`changed_facets` signal, so an aggregate projection is the natural shape and the
stream can push exactly the changed facets. Rationale:

- One coherent snapshot per context version - the UI renders the workspace from a
  single read rather than N racing fetches; avoids cross-tile version skew.
- The stream carries `changed_facets`, so the browser patches only affected tiles
  (matches selective regeneration / ADR-005 "latest relevant intent wins").
- #142 recommendations/selection slot in as `recommendations.*` and `selection.*`
  facets - no competing polling path.

Keep a **thin C fallback**: allow a per-tile GET only where a tile needs
independent paging or a write echo (e.g. selection POST returns its own result).
Do not build standalone read routes that duplicate a workspace facet.

## Proposed contract

Workspace projection (least-data, per context version):

```json
{
  "context_version": 7,
  "facets": {
    "conversation": { "messages": [ ... up to 50 ... ] },
    "shared_understanding": { "occasion": "...", "budget": "...", "recipient": "...",
      "style": "...", "flower_preference": "...", "timing": "...",
      "suggestions": [ ... up to 3 ... ] },
    "recommendations": { "items": [ { "product_id": "...", "available": true, ... } ] },
    "selection": { "product_id": "...", "card_message": "..." }
  },
  "ai_generated": true,
  "assistant_mode": "reference",
  "disclosure": "AI-generated interpretation; review and correct before ordering."
}
```

SSE event (unchanged wire format, `changed_facets`-scoped payload):

```
id: <event_id>
event: workspace
data: {"context_version":7,"changed_facets":["recommendations.items"],
       "facets":{"recommendations":{ ... only changed branch ... }}}
```

- `event_id` is monotonic per session; resume via `Last-Event-ID`/`?after=`.
- A full snapshot event is emitted on connect; deltas thereafter.
- Least-data shaping (`_least_data_projection`) still strips infra/sensitive fields.

## Internal API additions (in #144 scope)

- `GET /internal/v1/sessions/{id}/workspace` - aggregate least-data facet document
  at current context version.
- An event source for the stream backed by `changed_facets` (from the outbox /
  invalidation trail already written by `apply_experience_patch`), exposing
  `event_id`, `context_version`, `changed_facets`, and the changed facet branches.
- Wire `HttpOrchestration.workspace_projection` and `stream_events` to these; drop
  the `orchestration_unavailable` stubs.

## Non-goals

- `POST /api/v1/commands` / `accept_command` stays **deferred** (dedicated
  endpoints suffice). De-advertise it at the edge until a command-envelope
  standard is deliberately chosen. Not in #144.
- No workbook / requirement ID change; `check_coherence.py` unaffected.

## Impact on #142

- Recommendations/selection are delivered as workspace facets + stream deltas.
  #142 keeps `POST /api/v1/selection` (write) but its read surface becomes the
  `recommendations` / `selection` facets rather than a standalone
  `GET /api/v1/recommendations`.

### #142 refinement (implemented 2026-08-12)

The two facets have different natures, which the implementation makes explicit:

- **`recommendations` is a derived read projection, NOT stored state.** The
  `projection_dependency` registry already models `recommendations` as a
  projection_key regenerated from intent, so the workspace route computes it on
  read (`RecommendationService.preview`): rank the catalog against current intent
  and annotate each candidate with a real-time Available badge from a
  **non-authoritative** availability read (`InventoryAvailabilityService.availability`,
  which publishes no event, so it is safe on a GET). The stream's existing
  `recommendations` invalidation (emitted when intent changes) tells the browser
  to refetch. Recommendations are therefore **not** written via
  `apply_experience_patch`.
- **`selection` is authoritative state.** `POST /api/v1/selection` performs an
  authoritative selection-time revalidation (`inventory.validate` with
  `purpose="selection"`, which publishes + audits and rejects unavailable/stale),
  then writes the `decisions.product` facet (an existing `projection_dependency`
  facet - no migration) and emits `product.selected` in one versioned
  `apply_experience_patch` transaction, so the event fires exactly once at the new
  context version. The workspace `selection` facet reads `decisions.product`.

## Open questions

1. Snapshot-on-connect vs. client-supplied `after` for cold loads - default to
   full snapshot then deltas.
2. Do we need per-facet ETags/versions, or is the single `context_version`
   sufficient for optimistic tile patching? (Lean: single version is enough given
   `changed_facets`.)
3. Delivery/pricing tiles (M4/M5) - confirm they publish `changed_facets` on the
   same registry so the stream stays uniform.
