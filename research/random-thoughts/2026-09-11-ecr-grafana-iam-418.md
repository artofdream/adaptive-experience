# #418 GitLab OIDC EcrPush must include grafana + GetDownloadUrlForLayer

> **Tags**: #aea #second-brain #ecr #iam #oidc #grafana #418
> **Captured**: 2026-09-11
> **GitLab**: #418 (this MR) · leftover #414 ARM prove/apply stays open
> **Owners to inherit**: @aea-devsecops-platform, @aea-knowledge-guardian, @aea-mr-coordinator
> **This node is knowledge, not an apply ticket.** Do not `terraform apply` from this note. Do not flip live ECS to ARM64.

Inherits [[2026-09-10-path-b-multiarch-ecr-416]], [[2026-09-10-session-memory-log-path-b-multiarch-ecr-416]], [[2026-08-26-date-re-bus-and-agent-runner-image-roll]].

---

## What failed after !495 / #416

Required `build-ecr` on `main` built grafana via `scripts/ecr_multiarch_push.sh`
then died on push:

`User: aea-pilot-gitlab-ci is not authorized to perform: ecr:GetDownloadUrlForLayer`
on `arn:aws:ecr:us-east-1:737290977112:repository/aea-pilot/grafana`
(jobs 16438215440, 16435589756).

Repo `aea-pilot/grafana` already existed (`infra/aws/ecr.tf`). #416 added
the CI push; IAM did not move with it. Same class as #266 / !287
(`agent-runner` missing from `EcrPush`).

## Terraform vs live (non-binding probe)

Git `infra/aws/oidc.tf` `EcrPush` listed orchestration / bff / gateway /
agent-runner only, and omitted `ecr:GetDownloadUrlForLayer`. docker/buildx
multi-arch `--push` pulls existing dest-repo layers; that action is
required. Least privilege: named repo ARNs only — no `repository/*`.

This Cloud Agent did **not** `terraform apply`. DSO on **cts-ai** applies
the IAM role policy after merge, then re-runs `build-ecr` on `main`.
Do **not** apply #414 ARM64 task defs until imagetools inspect shows
both platforms (SOP in `infra/aws/README.md` § Image builds).

## Sequence after merge

1. MRC merges this IAM/docs MR (`Closes #418`).
2. DSO `terraform apply` on cts-ai — IAM only; no ARM cutover.
3. Re-run `build-ecr` on `main` (grafana + siblings).
4. Inspect `:latest` for amd64+arm64, then #414 leftover.
