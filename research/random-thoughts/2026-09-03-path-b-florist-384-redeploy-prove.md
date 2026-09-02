# Path B florist #384 — redeploy + prove attempt (2026-09-03)

> **Tags**: #aea #path-b #florist #384 #deploy-ecs #migration-023
> **When**: 2026-09-03 ~00:30 Europe/Berlin
> **Related**: [[2026-09-02-mrc-native-web-gap-closing-merges]] · [[2026-09-02-florist-operator-session-facts-383-385]] · [[2026-09-02-native-web-gap-closing-technical-handoff]]

## Goal

Get merged florist operator enrichment (!409 staff list + !418 session facts) live on `https://aea.artof.link` so #384 can be proven (channel allowlist `web` / `companion-android` / `unknown`).

## What was already on main

| Item | State |
|---|---|
| !409 `d7be014` | merged — staff-list card, catalog title, channel, paid/declined + **migration 023** |
| !418 `4098426` | merged — operator session facts (card / channel / total) |
| !426 docs SHA finalize | **merged** (green) during this pass |
| Last shop `deploy-ecs` | pipeline `2814723176` on `bd473b817e` (includes !409/!418) — force-new on `orchestration` `bff` `gateway` `relay` `consumer-workspace`; `/healthz` OK |

## Live prove (before migration apply)

| Check | Result |
|---|---|
| `GET /healthz` | 200 `{"status":"ok"}` |
| `GET /florist` + `/assets/florist.js` | 200 — UI already renders Channel / catalog title / paid (sample + live columns) |
| Session mint + CSRF | 201 / cookie `__Host-aea_session` |
| `GET /api/v1/operator/escalations` | 200 |
| `GET /api/v1/operator/sessions/{id}` | 200 — order has `order_id`/`status`; **`channel`/`total`/`payment_state` null** on pre-enrichment order; selection has `product_id` only |
| `GET /api/v1/operator/orders` | **HTTP 500** plain `Internal Server Error` (matches missing `orchestration.customer_order.aea_client`) |

Root cause class: `PostgresOrderStore.list_recent` / `checkout_view` `SELECT … aea_client` while **migration 023 not applied** on Path B RDS. `deploy-ecs` does **not** run migrations.

## Migration path (aea-pilot)

- SQL: `platform/migrations/023_order_operator_channel.sql` (`ADD COLUMN aea_client` + `schema_migration` v23)
- Apply: ECS `RunTask` override on `aea-pilot-orchestration` → `python platform/scripts/apply_migrations.py` (see `infra/aws/BOOTSTRAP.md`). Same private subnets + orchestration SG; `assignPublicIp=DISABLED`. Idempotent second pass OK.
- Not in GitLab `deploy-ecs` today (known gap; efficiency report already notes it).

## Redeploy attempt this pass

1. **AWS MCP** (`user-Aws-mcp`): `sts get-caller-identity` → **expired/invalid credentials**. Cannot list/force ECS or `RunTask` migrate from the box. No registered `cts-ai` machine via ListMachines.
2. **GitLab OIDC path**: API-created pipeline [`2814862151`](https://gitlab.com/artof-group/adaptive-experience-architecture/-/pipelines/2814862151) on `main` (`6f1e1d8720`) with auto `build-ecr` + `deploy-ecs` jobs created. Blocked behind long-running `android-build-debug` in verify before integration/deploy stages start.
3. Image roll alone will **not** clear the 500 until migration 023 lands.

## #384 close criteria (unchanged)

- `GET /api/v1/operator/orders` not 500
- Staff list / session summary show `channel` when present
- Fresh web checkout with `X-AEA-Client: web` → florist sees `channel=web` (or allowlisted equivalent)
- Do **not** close on sample UI or docs-only evidence

## Unblock needed

Refresh **Cursor AWS MCP / SSO credentials** for account used with `aea-pilot` (region `us-east-1`), then:

```text
1) ecs run-task … apply_migrations.py  (023)
2) optional: ecs update-service --force-new-deployment for orchestration bff gateway
3) re-prove orders + web checkout channel
4) comment + close #384 only if channel live
```

Or sponsor/DSO runs the same from a workstation with AWS CLI OIDC/profile.
