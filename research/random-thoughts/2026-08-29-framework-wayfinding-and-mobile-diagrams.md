# Framework wayfinding Table of Contents, in-page anchors, and mobile SVG diagram reflow

> **Tags**: #aea #second-brain #framework #wayfinding #a11y #ux #knowledge-first
> **Captured**: 2026-08-29
> **GitLab**: Related #287 (MRC merges; do not self-merge)
> **Owners to inherit**: @aea-ux-designer, @aea-senior-software-engineer, @aea-mr-coordinator

## Background & Decision

To address Phase 3 of the public site UX review:
1. **Automated Heading Anchor Slugs**: Added automated slug ID generation for H2 and H3 headings in `scripts/build_framework_site.py` (`id="formula"`, `id="six-layers"`, etc.).
2. **In-Page Jump Navigation**: Added lightweight, accessible Table of Contents bars (`.toc`) to `/schema` and `/comparison` so users on long pages can jump directly to specific layers and sections with smooth scrolling.
3. **Responsive Mobile SVG Stacking**: Added `@media (max-width: 480px)` container rules so SVG diagrams adapt cleanly to small smartphone viewports without horizontal clipping or overflow.

Existing IDs: [[2026-08-29-framework-nav-hygiene-and-freshness]], [[2026-08-29-public-voice-pass]], [[2026-08-29-sprint-coordination-finops-and-ux]].
