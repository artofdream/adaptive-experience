# FinOps #414 ARM64 cutover honesty (2026-09-11 Berlin evening)

> **Tags**: #aea #second-brain #finops #honesty #fargate #arm64 #ecr #knowledge-first
> **Captured**: 2026-09-11
> **GitLab**: #414 closed via **issue note** (no code MR for the live CLI roll) · #418 / !496 merged
> **Owners to inherit**: @aea-knowledge-guardian, @aea-cost-guardian, @aea-devsecops-platform, @aea-mr-coordinator
> **This node is knowledge, not an apply ticket.** Do not `terraform apply` from this note. Do not reopen or close #414 from a vault MR.

Later agents: treat this node as the live ARM status. Do **not** keep
reading [[2026-09-10-finops-414-partial-apply-honesty]] as “ARM still
blocked.” That 2026-09-10 reading is stale.

Inherits [[2026-09-10-finops-414-partial-apply-honesty]],
[[2026-09-10-path-b-multiarch-ecr-416]],
[[2026-09-11-ecr-grafana-iam-418]],
[[2026-09-10-finops-414-rds-arm64-apply-continuity]].

---

## Already true before this evening (do not re-apply)

- RDS `aea-pilot-postgres` is `db.t4g.small` (cts-ai AWS CLI, 2026-09-10).
- CloudWatch log retention 14d on the listed `/aea/aea-pilot/*` groups
  (same 2026-09-10 partial apply).
- Snapshot `aea-pilot-postgres-pre-t4g-small-20260910-2151` was
  **available** before that RDS modify.

## #418 / !496 then IAM (cts-ai)

#418 merged !496. IAM applied on **cts-ai**: `aea-pilot-gitlab-ci`
`EcrPush` includes grafana + `GetDownloadUrlForLayer`.

Main pipeline `build-ecr` succeeded after that IAM apply.

## Multi-arch inspect (blocker cleared)

`imagetools inspect` **PASS** `linux/amd64` + `linux/arm64` for:

- `aea-pilot/bff:latest`
- `aea-pilot/gateway:latest`
- `aea-pilot/orchestration:latest`
- `aea-pilot/agent-runner:latest`
- `aea-pilot/grafana:latest`

LiteLLM public tag `ghcr.io/berriai/litellm:main-latest` also has
amd64 + arm64.

## Live cutover on cts-ai (not full terraform apply)

#414 live cutover registered ARM64 `runtimePlatform` on **current**
task defs and `update-service`. This was **not** a full `terraform apply`
of all task defs (the 2026-09-10 13 add / 20 change / 9 destroy plan
stays unapplied).

Prove first, then the rest:

| Service | Task-def revision | Result |
|---|---|---|
| `grafana` | `:6` | prove first **PASS** |
| `bff` | `:3` | **PASS** |
| `gateway` | `:8` | **PASS** |
| `orchestration` | `:3` | **PASS** |
| `agent-runner` | `:3` | **PASS** |
| `consumer-workspace` | `:3` | **PASS** |
| `relay` | `:3` | **PASS** |
| `lily-reference-live-test` | `:2` | **PASS** |
| `litellm` | `:4` | **PASS** |

After the roll: `https://aea.artof.link` and `/florist` HTTP **200**.

## Tracker honesty

- #414 closed via **issue note**. There is no separate code MR for the
  live CLI roll. Do **not** reopen #414. Do **not** close #414 again
  from this vault MR.
- This honesty MR closes nothing (`Process-Exception: recurring-report`)
  unless a later session opens a **new** docs issue for README drift.

## Leftover (research-only this MR)

`infra/aws/README.md` § FinOps #414 and `infra/aws/BOOTSTRAP.md` still
describe the 2026-09-10 “ARM not applied / do not apply until inspect”
state. That operator copy is **stale**. This MR does not edit `infra/`.
Point operators at this node. A later DSO docs issue may refresh the
README.

Do **not** `terraform apply`. Do **not** purchase a Savings Plan from
this note. Do **not** move region. Keep MSK. Do not touch secrets.
