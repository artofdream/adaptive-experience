# Session Memory Log: GitLab OIDC EcrPush grafana (#418)

> **Tags**: #aea #session-memory #second-brain #ecr #iam #418
> **Captured**: 2026-09-11
> **Author**: `@aea-devsecops-platform` with `@aea-knowledge-guardian`
> **Related**: [[2026-09-11-ecr-grafana-iam-418]] · [[2026-09-10-path-b-multiarch-ecr-416]] · #418 · #416 · #414

## Why

After !495 / #416, required `build-ecr` failed pushing grafana:
`aea-pilot-gitlab-ci` denied `ecr:GetDownloadUrlForLayer` on
`aea-pilot/grafana`. Git `EcrPush` listed shop + agent-runner only.

## Decisions

- Add `aws_ecr_repository.grafana.arn` and `ecr:GetDownloadUrlForLayer`
  to `infra/aws/oidc.tf` `EcrPush`. Keep named ARNs (least privilege).
- Ratchet `scripts/test_iac_scan.py` so every `aws_ecr_repository` in
  `ecr.tf` must appear in `EcrPush`, plus the layer-download action.
- No `terraform apply` from this Cloud VM. After merge, DSO cts-ai
  applies IAM, then re-runs `build-ecr`. Do not start #414 ARM cutover
  from **this** IAM MR. **2026-09-11 evening:** that leftover **landed**
  — [[2026-09-11-finops-414-arm-cutover-honesty]].
- One `Closes #418`. #414 later closed via issue note (not this MR).

## Artifacts

- `infra/aws/oidc.tf`, `infra/aws/README.md` apply sequence
- `scripts/test_iac_scan.py` `test_ecr_push_covers_all_repos_and_layer_download`
- Vault: [[2026-09-11-ecr-grafana-iam-418]]
