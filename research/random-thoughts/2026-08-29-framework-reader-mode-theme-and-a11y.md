# Framework warm reader mode standard and a11y baseline

> **Tags**: #aea #second-brain #framework #reader-mode #a11y #ux #knowledge-first
> **Captured**: 2026-08-29
> **GitLab**: Related #284 (MRC merges; do not self-merge)
> **Owners to inherit**: @aea-ux-designer, @aea-knowledge-guardian, @aea-mr-coordinator

## Background & Decision

Sponsor requested warm editorial "reader mode" as the standard across `architecture.artof.link`.

### 1. Theme Standard (Option 2 — Adaptive Reader Mode)
- **Default (Light / Warm Paper)**:
  - Background: `--bg: #fbf8f1` (warm cream/paper)
  - Text: `--fg: #1c2024` (deep ink charcoal)
  - Muted: `--muted: #6b665c` (warm slate)
  - Rule: `--rule: #e3ded2` (subtle divider)
  - Accent: `--accent: #9c7c38` (warm gold / bronze)
  - Links: `--link: #1b6b93` (classic editorial reader blue)
  - Code: `--code-bg: #efebe0`
- **Dark Mode (`@media (prefers-color-scheme: dark)`)**:
  - Background: `--bg: #121417` (charcoal)
  - Text: `--fg: #e7e4dc` (ivory)
  - Accent: `--accent: #c4b08a` (gold)
  - Links: `--link: #d7c49a`

### 2. Accessibility Baseline (Issue #284)
- **Skip Link**: `<a href="#main" class="skip-link">Skip to content</a>` and `<main id="main">` for keyboard navigation.
- **Focus Rings**: `:focus-visible` with 2px outline and 2px offset on all interactive elements.
- **Tap Targets**: `display: inline-flex; min-height: 44px; align-items: center` for header and nav links.
- **Flex Wrap**: `nav.site` wraps cleanly on narrow mobile viewports.

Existing IDs: [[2026-08-29-public-framework-svg-diagrams]], [[2026-08-28-public-schema-page]], [[2026-08-28-architecture-artof-link-pages-sync]].
