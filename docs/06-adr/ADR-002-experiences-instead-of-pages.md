# ADR-002 — Experiences Instead of Pages

Status: Accepted

## Context
Conventional e-commerce moves the customer through a sequence of isolated pages,
losing context at each transition. The AEA goal is a persistent, context-
preserving workspace.

## Alternatives
- Page-centric navigation (catalog page, product page, checkout page).
- A single-page app that still swaps whole views per step.
- A persistent workspace where experiences (tiles) enter and leave in place.

## Decision
Use **experiences that enter and leave a stable workspace** instead of page-
centric navigation. Capabilities activate as tiles (T-01..T-09) within one
persistent Adaptive UI Workspace.

## Rationale
A single workspace preserves conversation, intent, and completed decisions across
the journey, enabling selective regeneration (FR-020) and continuity rather than
reloads.

## Consequences
- Tiles own one responsibility and a topic contract; the workspace manages
  arrangement.
- Navigation becomes activation/collapse of tiles, not page loads.
- State is shared and versioned by the Experience Orchestration Engine.
