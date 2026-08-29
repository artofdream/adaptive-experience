# Framework navigation hygiene, external links, and freshness timestamp

> **Tags**: #aea #second-brain #framework #ux #navigation #a11y #knowledge-first
> **Captured**: 2026-08-29
> **GitLab**: Related #286 (MRC merges; do not self-merge)
> **Owners to inherit**: @aea-ux-designer, @aea-knowledge-guardian, @aea-mr-coordinator

## Background & Decision

In response to independent UX review on `architecture.artof.link`, three navigation and wayfinding improvements were made:
1. **Nav Redundancy Removal**: Removed duplicate inline `[Home](index.html) · ...` breadcrumb rows from sub-pages (`schema.md`, `comparison.md`, `path-b.md`, `journal.md`). Top header navigation `<nav class="site">` is the clean single source of truth.
2. **External Link Distinction**: Added `a[href^="http"]:not([href*="architecture.artof.link"])::after { content: " ↗"; font-size: .8em; }` to visually distinguish leaving the framework site for external product `aea.artof.link`.
3. **Freshness & Observability**: Injected `Updated: 29 Aug 2026.` and active link to `https://aea.artof.link` into the site footer.

Existing IDs: [[2026-08-29-framework-reader-mode-theme-and-a11y]], [[2026-08-29-public-framework-svg-diagrams]], [[2026-08-28-public-schema-page]].
