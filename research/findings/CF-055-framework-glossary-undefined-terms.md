---
tags: #aea #coherence
finding_id: CF-055
status: in-mr
severity: low
source_assessment: 2026-08-29-framework-glossary-and-jargon
supersedes:
issue: "#300"
branch: docs/cf-055-framework-glossary
merge_request: "!331"
---

## Claim

The public framework site (docs/framework/*.md) uses several proper nouns
and internal conventions without ever defining them, and has no glossary or
first-use linking mechanism.

## Evidence

- docs/framework/comparison.md @ main ffe73a7: "Path B" (What this is),
  "CF-054" (What this is not / Core principles), "ID freeze" (Permissions)
  — none defined or linked anywhere in docs/framework/.
- schema.md defines "fourteen hats" (Roles) but nothing links to it from
  Comparison's own mentions.

## Intended fix

Add docs/framework/glossary.md (5 entries), register in PAGES, link first
on-page use of each term, add glossary to existing sibling link lists.

## Boundaries

- Included: glossary.md (new), comparison.md, path-b.md, index.md,
  schema.md, journal.md (link-only), build_framework_site.py (PAGES).
- Excluded: renaming Path B; reconciling Daily-brief/Claim-vs-probe naming
  (CF-056, separate MR); new SVG illustrations.
- ID impact: none.

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-29 | queued | Intake via assessment 2026-08-29-framework-glossary-and-jargon.md |
| 2026-08-29 | ready | Reproduced against main ffe73a7. |
| 2026-08-29 | in-mr | Applied via apply_cf_055.py; build_framework_site.py verified clean; committed on docs/cf-055-framework-glossary. |
| 2026-08-29 | in-mr | Reflowed glossary.md to match sibling line style; pushed; opened issue #300 and MR !331 (Closes #300). |

## Completion

- [x] Finding reproduced against updated main (ffe73a7)
- [x] Not already covered by an open issue or MR
- [x] GitLab issue created (#300)
- [x] Dedicated branch created from updated main
- [x] Focused fix committed
- [x] python scripts/build_framework_site.py passed
- [x] MR includes Closes #N, summary, and test plan (!331)
- [ ] MR merged
- [ ] Post-merge verification passed on main
