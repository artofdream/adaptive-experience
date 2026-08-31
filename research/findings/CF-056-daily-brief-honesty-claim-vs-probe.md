---
tags: #aea #coherence
finding_id: CF-056
status: in-progress
severity: low
source_assessment: 2026-08-29-framework-glossary-and-jargon
supersedes:
issue: "#342"
branch: cursor/docs-cf056-honesty-crosslink-e17d
merge_request:
---

## Claim

The same honesty incident is named two ways on the public framework site
("Daily-brief honesty" vs "Claim vs probe") with no cross-link.

## Evidence

- Canonical source: `docs/framework/comparison.md` ("What AEA claims here")
  uses "Daily-brief honesty"; `docs/framework/journal.md` titles the episode
  "Claim vs probe".
- Conflicting or incomplete path: neither page named the other title; the
  glossary Probe example pointed at both pages but did not say they are the
  same incident.
- Verification command: `python3 scripts/test_build_framework_site.py` and
  `python3 scripts/build_framework_site.py`.

## Intended fix

Cross-link the two names on the public pages. Do not restyle the shop.
Do not invent IDs. Do not batch with other tickets.

## Boundaries

- Included: `docs/framework/comparison.md`, `docs/framework/journal.md`,
  `docs/framework/glossary.md` (Probe example names both titles), queue row
  56, this finding note, builder unit test for the cross-link.
- Excluded: Path B / shop restyle; CF-054 clips; #320 / #323–#334; #308;
  Firebase; secrets; terraform; harness curator/reviewer/sensor (#338–#340).
- ID impact: none.

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-29 | queued | Intake via assessment 2026-08-29-framework-glossary-and-jargon.md |
| 2026-08-31 | investigating | Reproduced on origin/main `d6b39aa`: comparison.md line names Daily-brief honesty; journal.md `#claim-vs-probe` has no alias. |
| 2026-08-31 | in-progress | Cross-links applied on this branch. Issue #342 already open (intake). |

## Assessment history

| Assessment | Result | Notes |
|------------|--------|-------|
| 2026-08-29-framework-glossary-and-jargon | first-seen | Distinct from CF-055; one finding per MR |

## Completion

- [x] Finding reproduced against updated `main`
- [x] Not already covered by an open issue or MR
- [x] GitLab issue created (#342)
- [x] Dedicated branch created from updated `main`
- [ ] Focused fix committed and pushed
- [ ] Relevant checks passed
- [ ] MR includes `Closes #N`, summary, and test plan
- [ ] MR merged
- [ ] Post-merge verification passed on `main`
