# Session Memory Log: Path B multi-arch ECR (#416)

> **Tags**: #aea #session-memory #second-brain #ecr #arm64 #416
> **Captured**: 2026-09-10
> **Author**: `@aea-devsecops-platform` with `@aea-knowledge-guardian`
> **Related**: [[2026-09-10-path-b-multiarch-ecr-416]] · [[2026-09-10-finops-414-partial-apply-honesty]] · #416 · #414

## Why

#414 / !492 declared Fargate ARM64, but live `aea-pilot` ECR images were
linux/amd64 only. Applying ARM would brick Path B. Sponsor routed the
**build** track as #416. Prove + terraform apply stay leftover on #414.

## Decisions

- Smallest unlock: `docker buildx` manifest lists in existing
  `build-ecr` / `build-ecr-agent-runner`. Keep `:latest` + sha tags.
- Add Grafana to `build-ecr` (repo already existed; no CI push before).
- Do not change #331 committed pins from this Cloud Agent (no Docker Hub).
  Grafana CI uses official `10.4.0` tag via `AEA_GRAFANA_BASE`.
- Fail-closed inspect for LiteLLM is operator-side; this VM cannot reach
  GHCR. Call out official multi-arch tag vs “build our own ECR” if missing.
- No `terraform apply`. No live ARM flip **in the #416 MR**. One
  `Closes #416`. **2026-09-11 evening:** leftover ARM prove/apply
  **landed** — [[2026-09-11-finops-414-arm-cutover-honesty]]. #414
  closed via issue note.
- image-scan stays native amd64 (do not double QEMU scan time).

## Artifacts

- `scripts/ecr_multiarch_push.sh`, `scripts/test_ecr_multiarch_push.py`
- `.gitlab-ci.yml` `build-ecr` / `build-ecr-agent-runner`
- `platform/docker/Dockerfile.grafana` ARG
- `infra/aws/outputs.tf` `ecr_grafana_url`, README / BOOTSTRAP SOP
- Vault: [[2026-09-10-path-b-multiarch-ecr-416]]
