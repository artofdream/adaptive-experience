# ADR-005 — Latest Relevant Intent Wins

Status: Accepted

## Context
The workspace is asynchronous and event-driven. Multiple in-flight responses
(recommendations, pricing, delivery) can return out of order after the customer
has already changed their intent, risking stale data overwriting newer choices.

## Alternatives
- Last-write-wins by arrival time (accept whatever returns last).
- Block the UI until each in-flight request resolves.
- Version the context and reject responses that do not match the active version.

## Decision
**Older in-flight responses may finish but cannot overwrite newer intent.** Each
response carries the context version; responses whose version does not match the
active experience state are rejected (FR-022).

## Rationale
Context versioning preserves the customer's most recent decisions without
blocking the workspace, and keeps completed choices stable during selective
regeneration (FR-020, NFR-005). It is the core correctness guarantee of the
adaptive workspace.

## Consequences
- The Experience Orchestration Engine increments and stamps a context version on
  every intent change.
- Domain services echo the context version; stale responses are dropped, not
  rendered.
- Auditing must record context version per message (NFR-016).
