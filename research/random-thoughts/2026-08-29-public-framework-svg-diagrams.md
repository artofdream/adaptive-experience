# Vector SVG architecture diagrams on architecture.artof.link

> **Tags**: #aea #second-brain #framework #diagrams #svg #knowledge-first
> **Captured**: 2026-08-29
> **GitLab**: Related #280 (MRC merges; do not self-merge)
> **Owners to inherit**: @aea-knowledge-guardian, @aea-product-owner, @aea-mr-coordinator

## Background & Decision

`architecture.artof.link` requires clean, visual architecture schematics (formula, six layers, execution loop).

Client-side Mermaid JS was explicitly rejected:
1. **Zero-Dependency Alpine Builder**: `scripts/build_framework_site.py` is a pure Python standard-library generator running in a minimal `python:3.12-alpine` CI runner. Server-side compilation would introduce Node.js and Chromium build bloat.
2. **Performance & CLS**: Client-side JavaScript introduces script-eval overhead, CSP complexity, and Cumulative Layout Shift (CLS) during diagram hydration.
3. **Aesthetic & Theme Harmony**: Custom SVGs match the exact `#121417` charcoal and `#c4b08a` gold palette of the site, scaling cleanly across mobile (9:16) and desktop (16:9) viewports.

## Assets Added

- `docs/framework/assets/formula.svg`: Visual 3-pillar formula ($\text{Shared Understanding} + \text{Domain Services} + \text{Outer Harness}$).
- `docs/framework/assets/six-layers.svg`: Stacked 6-layer architecture schematic.
- `docs/framework/assets/the-loop.svg`: 4-step execution loop ($\text{Interpret} \to \text{Act} \to \text{Verify} \to \text{Remember}$) with feedback.

## Verified Links

Embedded in allowlisted markdown at `docs/framework/index.md` and `docs/framework/schema.md`.

Existing IDs: [[2026-08-28-public-schema-page]], [[2026-08-28-public-journal]], [[2026-08-28-architecture-artof-link-pages-sync]].
