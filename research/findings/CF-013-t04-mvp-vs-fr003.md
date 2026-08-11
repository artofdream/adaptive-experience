# CF-013 — T-04 wireframe vs FR-003 Future scope

tags: #aea #coherence-finding
status: queued
finding_id: CF-013
severity: medium
issue: #104

## Claim

MVP T-04 surfaces in local wireframes and Figma fidelity notes show Flower Type,
Colour, Size, Ribbon, and Gift Card, while published scope says T-04 MVP is
product selection, basic options (arrangement, size), and card message —
advanced customization (FR-003: flower type, color, size, messages) is Future.

## Evidence

- `implementations/florist/wireframes/adaptive-workspace-mvp.svg` (T-04 fields)
- `figma/README.md` MVP fidelity bullets
- `docs/03-functional-design/functional-design.md` T-04 MVP vs FR-003 Future
- `docs/02-business-analysis/requirements.md` FR-003 Future
- `docs/07-roadmap/roadmap.md`
- GitLab #104 — ADR-006 Define MVP customization boundary

## Intended fix

Resolve via ADR-006 (#104): either (a) document which T-04 fields are MVP
basic options vs Future FR-003 affordances in the wireframe, or (b) simplify
MVP wireframe/Figma to match published basic options + card message only.
Keep FR IDs unchanged unless an explicit archive change is approved.
