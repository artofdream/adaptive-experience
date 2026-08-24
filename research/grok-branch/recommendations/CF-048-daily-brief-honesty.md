# Recommendation: CF-048 — Honest daily-brief generator

> **Finding:** CF-048 (High)  
> **Workstream:** `grok` (markdown only — manual GitLab promotion)  
> **Suggested owner on GitLab:** `@aea-coherence-guardian`  
> **Suggested branch name:** `fix/cf-048-daily-brief-honesty`  
> **Do not merge from this sandbox.**

## Problem

`scripts/generate_daily_brief.py` embeds static claims:

- `**15/16 Milestones Completed (93.75%)**`
- Active focus M15 “Edge SSR & Sub-100ms LCP”
- Process text asserting pre-rendered HTML and sub-100ms LCP guarantees

Regeneration overwrites any honest status with unsupported delivery claims. Dual writers (`YYYY-MM-DD.md` vs `YYYY-MM-DD-daily-brief.md`) and historical MR !270 path collision increase risk of clobber.

## Desired outcome

1. Milestone / guard status in the brief is **derived from evidence**, not hardcoded.
2. No claim of browser LCP or SSR unless measurement and implementation support it.
3. Single clear ownership of the daily-brief path (document which filename is canonical).

## Proposed change (focused)

### A. `scripts/generate_daily_brief.py`

- Remove hardcoded “15/16” and M15 SSR/sub-100ms narrative blocks.
- Derive:
  - Guard line from actual `run_all_guards.py` stdout (already partially done).
  - Milestone summary from a small, explicit parse of `docs/07-roadmap/roadmap.md` **or** a conservative static table that only lists milestones as “Completed” when an agreed evidence path exists (prefer: do not auto-promote M14–M18 as complete).
- For M15 language: use neutral wording, e.g. “Edge static shell + TTFB audit scripts (browser LCP / SSR not claimed).”
- Keep generation target path documented in script docstring; prefer one canonical filename.

### B. Path ownership (docs note, same MR or tiny follow-up)

In `research/daily-briefs/` or script header, state:

- Canonical generator output: `YYYY-MM-DD-daily-brief.md` (from `generate_daily_brief.py`)
- Session/activity reports may use `YYYY-MM-DD.md` but must not be overwritten by the generator
- Close or supersede any open MR that collides on these paths before merge

### C. Out of scope for this MR

- Implementing real SSR or Web Vitals LCP (CF-049 / product work)
- Changing roadmap milestone rows (separate MRs for CF-049, CF-052, CF-053)
- Archive/workbook ID changes

## Acceptance checks

- [ ] `python scripts/generate_daily_brief.py` produces a brief **without** “15/16” or “sub-100ms LCP” as asserted shipped fact
- [ ] Guard section still reflects live runner output
- [ ] `python scripts/run_all_guards.py` remains 14/14 (or documented skip)
- [ ] No second finding mixed into the same branch

## Manual GitLab steps

1. Create issue linking CF-048 (or use existing).
2. Branch `fix/cf-048-daily-brief-honesty` from `origin/main`.
3. Apply A (+ B if small).
4. Open focused MR; hand to `@aea-mr-coordinator` when green.
5. After merge, optional: copy resolution note back under `research/grok-branch/findings/` as closed.

## References

- `scripts/generate_daily_brief.py`
- `scripts/audit_lcp_performance.py` (related claim surface; do not fix in this MR)
- `docs/07-roadmap/roadmap.md` (M15 row)
- `research/coherence-findings-loop.md`
- Prior assessments: Codex CF-048 intake; Grok assessment 2026-08-23
