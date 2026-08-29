# Sprint Coordination: FinOps Right-Sizing, UX Wayfinding, and Governance Phasing

> **Tags**: #aea #second-brain #scrum #project-management #finops #delivery #coordination
> **Captured**: 2026-08-29
> **Owners to inherit**: @aea-project-manager, @aea-devsecops-platform, @aea-ux-designer, @aea-cost-guardian, @aea-mr-coordinator

## Executive Summary & Sponsor Authorization

Project Sponsor explicitly authorized the August FinOps recommendations and sequencing:
1. **AWS ECS Fargate ARM64 Migration (Issue #282)** — Graviton compute optimization (20% compute savings).
2. **RDS PostgreSQL Right-Sizing** — Downscale `db.t4g.medium` -> `db.t4g.small` (50% database compute savings).
3. **Pages UX Wayfinding & Mobile Diagram Reflow (Issue #287)** — In-page anchor IDs, Table of Contents, and mobile `<480px` diagram responsiveness.
4. **Knowledge Guard Posture (Issue #294 / MR !323)** — Fix wikilinks for copyright rule.

## Phasing & Ownership Matrix

| Sprint Item | Owning Stakeholder | Surface / Files | Delivery Artifact |
|---|---|---|---|
| **P1.1: FinOps Fargate ARM64** | @aea-devsecops-platform | `infra/aws/ecs.tf`, `.gitlab-ci.yml` | MR against #282 |
| **P1.2: FinOps RDS Right-Sizing** | @aea-devsecops-platform | `infra/aws/variables.tf`, `infra/aws/rds.tf` | MR for RDS scaling |
| **P1.3: Pages Wayfinding & Mobile SVGs** | @aea-ux-designer / @aea-senior-software-engineer | `scripts/build_framework_site.py`, `docs/framework/` | MR against #287 |
| **P1.4: Knowledge Graph Fix** | @aea-knowledge-guardian | `research/random-thoughts/2026-08-29-copyright-quotation.md` | MR !323 fix |
| **P2: Strategic Harness Evaluations** | @aea-ai-engineer / @aea-product-owner | `docs/`, `research/` | Issues #288–#292 |

Existing IDs: [[2026-08-29-framework-reader-mode-theme-and-a11y]], [[2026-08-29-public-voice-pass]], [[2026-08-29-journal-vector-svg-diagrams]].
