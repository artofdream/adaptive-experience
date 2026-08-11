# CF-014 — Misnumbered Accepted ADR stubs collide with ADR-006/007

tags: #aea #coherence-finding
status: in-mr
finding_id: CF-014
severity: high
issue: #110
mr: !56
branch: docs/cf-014-quarantine-misnumbered-adr-stubs

## Claim

Untracked files `ADR-008`…`ADR-012` under `docs/06-adr/` carry H1 titles
ADR-006…010 and Status Accepted, colliding with Proposed ADR-006/007 and
blocking GitLab gate numbers #104–#108.

## Evidence

- Former `docs/06-adr/ADR-008-postgresql-pgvector.md` → H1 ADR-006 Accepted
- Former `docs/06-adr/ADR-009-kafka-event-backbone.md` → H1 ADR-007 Accepted
- Former `docs/06-adr/ADR-010`…`ADR-012` similarly mis-titled

## Fix applied

Moved content to `research/adr-candidates/` as Draft promotion candidates
(topic filenames, no colliding ADR numbers). `docs/06-adr/` retains only
published ADR-001…005 on main (ADR-006/007 Proposed drafts remain local for
later CF-013/CF-017).
