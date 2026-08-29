# Coherence assessment — 2026-08-29

tags: #aea #coherence-assessment
status: intake
assessed_ref: ffe73a7640a66e8f6dfdbd4116a276b458b1ed76
assessed_by: Claude (Cowork), at user's request, first-time-reader comprehension pass

## Scope

- Paths reviewed: docs/framework/index.md, schema.md, comparison.md, path-b.md, journal.md (main @ ffe73a7, includes docs/281-public-voice-pass and ux/287-wayfinding-toc-mobile-svgs).
- Checks executed: manual first-time-reader read-through of all 5 published pages (live site, then re-verified against current main source directly).
- Exclusions: CSS/nav/a11y (owned by concurrent work today), Path B live-app UX (CF-054, out of scope here).

## Findings

| Finding ID | Claim | Severity | Evidence paths | Existing issue / MR |
|------------|-------|----------|----------------|---------------------|
| CF-055 | Public framework docs use undefined proper nouns/conventions (Path B, CF-NNN, ID freeze) with no glossary or first-use links | Low | docs/framework/comparison.md, path-b.md | none |
| CF-056 | Same incident named two different ways across pages (Daily-brief honesty vs. Claim vs probe) with no cross-link | Low | docs/framework/comparison.md, journal.md | none |

## Intake reconciliation

| Finding ID | Decision | Queue status | Reason |
|------------|----------|--------------|--------|
| CF-055 | new | queued -> ready (remediated this iteration) | No equivalent row found. |
| CF-056 | new | queued (not remediated) | Distinct claim; one finding per branch/MR. |

## Assessment conclusion

- New findings added: CF-055, CF-056
- Regressions reopened: none
- Duplicates linked: none
- Queue reordered: no
- Next queued finding: CF-055 (remediated here); CF-056 remains for a separate iteration
