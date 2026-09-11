# #418 GitLab OIDC EcrPush must include grafana + GetDownloadUrlForLayer

> **Tags**: #aea #second-brain #ecr #iam #oidc #grafana #418
> **Captured**: 2026-09-11
> **GitLab**: #418 / !496 merged · leftover #414 ARM prove/apply **done 2026-09-11**
> **Owners to inherit**: @aea-devsecops-platform, @aea-knowledge-guardian, @aea-mr-coordinator
> **This node is knowledge, not an apply ticket.** Do not `terraform apply` from this note.

**2026-09-11 Berlin evening:** IAM applied on cts-ai; `build-ecr` on
`main` succeeded; inspect PASS; #414 ARM cutover landed. Canonical:
[[2026-09-11-finops-414-arm-cutover-honesty]]. The “do not flip live
ECS / leftover stays open” lines below are **stale**.

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

## Sequence after merge (completed 2026-09-11)

1. MRC merged this IAM/docs MR (`Closes #418` / !496).
2. DSO applied IAM on cts-ai — `aea-pilot-gitlab-ci` `EcrPush` includes
   grafana + `GetDownloadUrlForLayer`.
3. `build-ecr` on `main` succeeded after IAM.
4. Inspect `:latest` PASS amd64+arm64 (shop + grafana + LiteLLM GHCR);
   then #414 leftover cutover — see
   [[2026-09-11-finops-414-arm-cutover-honesty]].
