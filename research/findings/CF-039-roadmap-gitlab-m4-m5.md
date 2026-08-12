# Coherence finding — Roadmap vs GitLab M4/M5 milestone FR placement

tags: #aea #coherence
finding_id: CF-039
status: queued
severity: medium
source_assessment: research/assessments/2026-08-12-pre-m4-hygiene-reconciliation.md
issue:
branch:
merge_request:

## Claim

`docs/07-roadmap/roadmap.md` M4/M5 requirements coverage disagrees with GitLab
milestone assignments for FR-013, FR-015, FR-018, and NFR-014.

## Evidence

- Roadmap M4: FR-013, FR-014, FR-015
- Roadmap M5: FR-018, FR-019; NFR-013, NFR-014
- GitLab: #32 FR-013 → M5; #34 FR-015 → M6; #37 FR-018 → M4; NFR-014 also in Future

## Intended fix

Align either GitLab milestones or roadmap coverage columns (and NFR-014 Future
vs M5) so M4 planning has one authoritative placement.

## Boundaries

- Included: roadmap and/or GitLab milestone metadata
- Excluded: implementing M4 features
- ID impact: existing IDs only
