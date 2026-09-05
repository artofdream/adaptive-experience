---
tags: #aea #coherence
finding_id: CF-056
status: verified
severity: low
source_assessment: 2026-08-29-framework-glossary-and-jargon
supersedes:
issue: "#342"
branch: cursor/docs-cf056-queue-verified-59d4
merge_request: "!361"
verified_on_main: 0783d3d
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

Post-merge verify 2026-09-05 against `origin/main` `3ee4191` (descendant of
!361 merge `0783d3d`, 2026-08-31, `#342` closed):

- `comparison.md` still says Daily-brief honesty and links
  `journal.html#claim-vs-probe`.
- `journal.md` `#claim-vs-probe` still aliases Daily-brief honesty and links
  `comparison.html#what-aea-claims-here`.
- Glossary Probe example had dropped the dual-title sentence after the later
  plain-English reformulation; restored in this verify MR so !361's intended
  three-page alias remains.
- `python3 scripts/test_build_framework_site.py -k cf056` PASS.
- `#342` stays closed. Do not reopen. Relates to `#342` / `!361`.

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
| 2026-08-31 | in-mr | Cross-links applied. Issue #342. MR !361. |
| 2026-09-05 | verified | !361 merged `0783d3d`. Re-probed on `origin/main` `3ee4191`: comparison↔journal still linked. Glossary Probe dual-title restored. Queue row 56 set `verified`. CF-054 stays `regressed`. |

## Assessment history

| Assessment | Result | Notes |
|------------|--------|-------|
| 2026-08-29-framework-glossary-and-jargon | first-seen | Distinct from CF-055; one finding per MR |
| 2026-09-05 post-merge verify | resolved | Pages still cross-link; queue lag `in-mr` after merge is honesty drift, not a new claim |

## Completion

- [x] Finding reproduced against updated `main`
- [x] Not already covered by an open issue or MR
- [x] GitLab issue created (#342)
- [x] Dedicated branch created from updated `main`
- [x] Focused fix committed and pushed
- [x] Relevant checks passed
- [x] MR includes `Closes #N`, summary, and test plan
- [x] MR merged
- [x] Post-merge verification passed on `main`
