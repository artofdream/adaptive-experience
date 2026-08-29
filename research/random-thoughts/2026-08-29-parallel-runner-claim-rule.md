# Adopted: parallel-runner path and scope claim (29 Aug 2026)

> **Tags**: #aea #second-brain

Related: #301. Adopted as sensor from #297 (sponsor 29 Aug 2026 14:25 Europe/Berlin). Not a claim board. Not a CI gate. Not a claim that AEA is antifragile.

## The rule

Before a runner opens an MR it claims, in the MR description:

1. the file paths it will touch, and
2. the issue's "done when."

Fail closed if another **open** MR already claims those paths.
Fail closed if the diff exceeds evaluate-only or confirm-only.

A status word is still a claim. It needs a probe in the same session. MRC stays a merge hat, not a GitLab username. GitLab Duo auto-reviewer is noise.

## How to fail closed (this slice)

Human and runner check, before `save_merge_request`:

- `list_merge_requests` state=opened. If any open MR already touches the claimed paths, stop.
- Read the issue. If it says evaluate-only or confirm-only, the MR may not implement past that ceiling.

A later issue may add a computational check if this miss repeats. This ticket does not.

## What this is not

- Not CONSTRAINTS.md (#289). Not a DATE_RE edit (#291). Not a judge model (#292).
- Not a Kimi swarm. Not a new CF-id. Not shop restyle. Not 3DX Lab.
- Dual-viewport after CSS remains Unknown. Pipeline green is not live Fargate ARM64.
