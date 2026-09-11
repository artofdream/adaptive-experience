# Session Memory Log: FinOps #414 ARM64 live cutover honesty

> **Tags**: #aea #session-memory #second-brain #finops #414 #arm64
> **Captured**: 2026-09-11
> **Author**: `@aea-knowledge-guardian` with `@aea-devsecops-platform`
> **Related**: [[2026-09-11-finops-414-arm-cutover-honesty]] · [[2026-09-10-finops-414-partial-apply-honesty]] · [[2026-09-11-ecr-grafana-iam-418]] · #414 · #418 · !496

## Why

Vault notes from 2026-09-10 / this morning still said ARM64 Fargate was
blocked (amd64-only ECR, then IAM/`build-ecr` leftover). The live
cutover landed on cts-ai this Berlin evening. Without a new node, later
agents would keep writing “ARM not applied.”

## Decisions

- Knowledge / DATE_RE honesty only. No `terraform apply`. No secrets.
  No reopen/close of #414 from this MR.
- Record the actual apply path: register ARM64 `runtimePlatform` on
  current task defs + `update-service`, **not** a full terraform apply
  of all task defs.
- grafana `:6` prove first, then the listed sibling revisions.
- Prefer `Process-Exception: recurring-report` (or a new docs issue).
  Do not `Closes #414`.
- Leave `infra/aws/README.md` / `BOOTSTRAP.md` for a later DSO docs
  issue; this MR stays research-only.

## Artifacts

- Vault: [[2026-09-11-finops-414-arm-cutover-honesty]]
- Hand-review line on `research/daily-briefs/2026-09-11.md`
- Addendums on the 2026-09-10 / #418 nodes that still said ARM was open
