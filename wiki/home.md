# Adaptive Experience Architecture — Wiki Home

This wiki is the navigable companion to the repository. It summarises each area and links to the canonical source files in `docs/`, `implementations/`, `research/`, and `archive/`.

## Contents

| Page | What it covers |
|------|----------------|
| [Product Vision](product-vision) | North star, business goals, and design principles |
| [Business Analysis](business-analysis) | Business goals, epics, user stories, and requirements |
| [Functional Design](functional-design) | Tile catalog, overlays, and functional flow |
| [Technical Architecture](technical-architecture) | Core elements, domain services, message bus, and topic groups |
| [UX Design Guide](ux-design-guide) | Tile-to-surface mapping, typography, and layout rules |
| [Architecture Decision Records](architecture-decision-records) | ADR-001 through ADR-005 |
| [Roadmap](roadmap) | MVP, MVP+, and Future scope |
| [Florist Reference Design](florist-reference-design) | Lily's Florist implementation area |
| [Coherence Workflow](coherence-workflow) | Coherence guard, findings loop, and Claude–Obsidian loop |
| [Source of Truth & Archive](source-of-truth) | Canonical workbook, CSV export, and CI guard |

## Quick orientation

- **Canonical requirements** live in `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx` (7 BG · 7 EP · 23 US · 17 NFR-US · 40 requirements). Never invent IDs outside this model.
- **Published architecture** lives in `docs/` and `implementations/`; edit via focused merge requests.
- **Working notes** live in `research/`; they are not canonical until promoted.
- **CI coherence guard** (`scripts/check_coherence.py`) fails if markdown ID counts diverge from the workbook.
