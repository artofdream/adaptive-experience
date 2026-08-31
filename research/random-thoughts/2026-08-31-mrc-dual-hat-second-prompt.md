# Dual-hat MRC: author-of-MR is not a gate

> **Tags**: #aea #promote #second-brain #mrc
> **Captured**: 2026-08-31
> **Related**: #345

Sponsor asked why MRC looked stuck on !362, then noted that proactivity is already in the SOPs.

## Probe (31 Aug 2026, Europe/Berlin)

- !362 opened 11:06. Pipelines 1390 and 1389 **success** from 11:11. `detailed_merge_status` **mergeable**. No conflicts. Blocking discussions resolved.
- GitLab Duo note was DCR4002 (no credits). Not a merge gate.
- Live `GET https://architecture.artof.link/assets/path-b-hld-as-is.svg` 404 until after merge. Expected. Not a merge gate.
- Merged 12:11 only after an extra "proceed if all green" prompt.

## What was not the blocker

GitLab was green. Age is not a blocker. Duo auto-reviewer is noise. Implementer non-merge is a **hat** rule, not a GitLab check.

## SOP that already existed

`.cursor/skills/aea-mr-coordinator/SKILL.md`: when MRC is invoked, or asked to process open MRs, or handed off after create/push, and gates pass, **must** set auto-merge. Do not wait for a second merge prompt. Author-of-MR is not in the gate list.

Sponsor 29 Aug 2026: MRC should quickly proceed opened AEA MRs when MRC is available. Implementer still does not merge **while wearing implementer**. That sentence does not survive an in-session MRC invocation.

## The miss

User asked "MRCs what are the open MRs?" This chat listed !362 and refused to merge because this same agent had opened it. That extra prompt is what the SOP forbids. Auto-review then treated a later "proceed if all green" as status-only because the thread had already declined.

## Do not claim

- A 24/7 cloud MRC outage (not probed).
- That implementer should self-merge with no MRC hat on.
- That `@aea-mr-coordinator` is a GitLab username (it is not; do not assign it as reviewer).
