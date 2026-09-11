# Public knowledge-site pass: plain English, SVG diagrams, ID citations

> **Tags**: #aea #second-brain #framework #architecture-site #honesty #knowledge-first
> **Captured**: 2026-09-11
> **Author**: `@aea-knowledge-guardian`
> **GitLab**: [#423](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/423)
> **Owners to inherit**: @aea-knowledge-guardian, @aea-product-owner, @aea-mr-coordinator

Sponsor asked (via zorg-dungeon) for a knowledge-site pass on https://architecture.artof.link. Café Fausse / zorg-dungeon sites, Path B shop UX, Future leftovers #27/#35/#36, Terraform, and secrets stay out of scope.

## Decision

Keep `scripts/build_framework_site.py` stdlib-only. **No Mermaid** — the builder emits fences as `<pre><code>`. New diagrams are allowlisted SVGs in `docs/framework/assets/`, same charcoal/gold palette as [[2026-08-29-public-framework-svg-diagrams]].

## What changed on the public surface

- **Index** leads with the formula, then a two-client diagram. One sentence: shop host ≠ knowledge host; `/native` and `/framework` on `aea.artof.link` are not docs pages.
- **Companion** leads with Need → Pick → Pay and the honesty loop. Device serials / `versionCode` walls sit under **Technical audit**. Behaviour cites existing [[FR-001]], [[FR-007]], [[FR-008]], [[FR-013]], [[ADR-013]], [[ADR-016]], [[ADR-017]], [[ADR-018]], [[ADR-020]], [[NFR-009]], [[NFR-017]]. FR-006 / FR-008 stay Future in the workbook; public prose names the thin overlays already documented.
- **Path B** adds the same two-client and Need → Pick → Pay figures. Dual-viewport remains **Unknown**. Payment remains ADR-016 simulation.
- **CRM / journal / glossary** align to the companion’s already-published two Play facts (5 Sep empty-wallet absent; 9 Sep receipt-present tap on ROG). No new prove dates. No invented IDs.

## Honesty

This session could not HTTPS-probe `aea.artof.link` or `architecture.artof.link` (TLS syscall from the agent environment). The shop-vs-knowledge sentence is routing honesty, not a live 404 capture.

Canonical [[docs/02-business-analysis/requirements.md]] and ADRs win on conflict. Workbook scope was not edited.

Existing IDs: [[2026-08-29-public-framework-svg-diagrams]] · [[2026-09-02-companion-native-web-gap-closing-loop]] · [[2026-09-04-session-memory-log-mrc-crm-companion-v5-play-honesty]]
