# Design note — FR-012 inventory forecast (#31)

status: implemented (thin path)
for_issues: "#31 (FR-012 Inventory forecasting)"
affects: "Inventory authority + local florist operator console; does not replace FR-011"
date: 2026-08-15

## Decision

Analyze validated inventory snapshot history and recommend replenishment on
the existing `/florist` manager console. Persist observations when
`InventoryAvailabilityService.record` applies a snapshot. Publish
`inventory.forecast.ready`.

FR-012 stays Future in the requirements source of truth. NFR-010 stays
Future; this slice uses only current, validated snapshots and refuses to
forecast from stale or single-point history.

## Not in this slice

ML / seasonal demand models, purchase-order writes, production warehouse
feeds, or changing customer T-03 / FR-011 fail-closed selection.
