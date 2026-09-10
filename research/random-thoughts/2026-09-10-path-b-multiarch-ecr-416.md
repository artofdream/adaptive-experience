# Path B multi-arch ECR builds (#416) — build track only

> **Tags**: #aea #second-brain #finops #ecr #arm64 #fargate #honesty #knowledge-first
> **Captured**: 2026-09-10
> **GitLab**: #416 (this MR closes the **build** track) · #414 leftover prove/apply stays open
> **Owners to inherit**: @aea-devsecops-platform, @aea-cost-guardian, @aea-knowledge-guardian, @aea-mr-coordinator
> **This node is knowledge, not an apply ticket.** Do not `terraform apply` from this note. Do not flip live ECS to ARM64.

Inherits [[2026-09-10-finops-414-partial-apply-honesty]], [[2026-09-10-finops-414-rds-arm64-apply-continuity]], [[2026-09-05-session-memory-log-331-image-digest-pins]].

---

## What was true on live ECR (2026-09-10)

Confirmed amd64-only (single manifest / amd64 index):

- `aea-pilot/bff`, `aea-pilot/gateway`, `aea-pilot/orchestration`
- `aea-pilot/grafana` index listed amd64 only
- `agent-runner` also needed a dual-arch list before ARM cutover

Root cause in git: `.gitlab-ci.yml` `build-ecr` / `build-ecr-agent-runner`
used `docker build` + `docker push` on GitLab SaaS amd64. That always
publishes a **single-arch** manifest even when the FROM pin is a
multi-arch index. Grafana had no CI push job at all (ECR repo existed;
`:latest` was still amd64-only).

Applying #414 `runtime_platform` ARM64 against those tags would fail
pulls/starts and take Path B down.

## What this MR changes (build track)

- `scripts/ecr_multiarch_push.sh` — `docker buildx` + QEMU binfmt,
  `--platform linux/amd64,linux/arm64`, `--push` of `:latest` and
  `$CI_COMMIT_SHA` (same tag contract as before).
- `build-ecr` now also builds Grafana (`AEA_ECR_GRAFANA`, or derive from
  `AEA_ECR_GATEWAY` …`/gateway` → `…/grafana`).
- Grafana Dockerfile keeps the #331 amd64 pin as `AEA_GRAFANA_BASE`
  default. CI overrides to official `grafana/grafana:10.4.0` (Hub
  publishes amd64+arm64). Do not invent an index digest from a Cloud
  Agent that cannot reach Docker Hub.
- If a #331 FROM pin inspects as single-arch, CI falls back to the same
  **tag** for that ECR push only. Committed pins stay. Record an index
  digest on the next pin cadence if a WARN appears.
- image-scan (#332) still builds native amd64 only and does not push.
- No `terraform apply`. No live ARM64 task-def roll.

## Verify before ARM cutover

From a host that can reach ECR (DSO laptop / GitLab job):

```bash
docker buildx imagetools inspect "$AEA_ECR_ORCHESTRATION:latest"
docker buildx imagetools inspect "$AEA_ECR_BFF:latest"
docker buildx imagetools inspect "$AEA_ECR_GATEWAY:latest"
docker buildx imagetools inspect "$AEA_ECR_AGENT_RUNNER:latest"
docker buildx imagetools inspect "${AEA_ECR_GRAFANA:-$AEA_ECR_GATEWAY/../grafana}:latest"
docker buildx imagetools inspect ghcr.io/berriai/litellm:main-latest
```

Each list must show `linux/amd64` **and** `linux/arm64`. SOP copy:
`infra/aws/README.md` § Image builds.

## LiteLLM (public image, not ECR)

Path B uses `ghcr.io/berriai/litellm:main-latest`
(`infra/aws/variables.tf` `litellm_image`; same tag as
`edge/docker-compose.litellm.yml`). #331 keeps it as an expiring
exception (no digest) through 2026-10-05.

This Cloud Agent **cannot** reach `ghcr.io` / Docker Hub (egress
allowlist). Do not treat that as “LiteLLM has no arm64.” Official
LiteLLM GHCR tags are published multi-arch; **confirm with imagetools
inspect** on a host that can pull GHCR before ARM apply.

If inspect lacks `linux/arm64`:

1. Do **not** pin a guessed tag.
2. Prefer an official release tag whose inspect shows both platforms.
3. Or build our own `aea-pilot/litellm` with the same buildx helper and
   point `litellm_image` at that ECR URL (separate issue; not this MR).

Missing LiteLLM arm64 is a **cutover blocker**.

## Leftover (do not close #414 from this MR)

#416 issue text also asked to prove one service on ARM64 Fargate and
then apply the #414 task defs. That is **not** done here. Leave #414
open. After merge + inspect, DSO proves one service then applies.
Do not auto-close #414.

Do **not** merge from a Cloud Agent. Do **not** touch secrets/keystores/`.env`.
