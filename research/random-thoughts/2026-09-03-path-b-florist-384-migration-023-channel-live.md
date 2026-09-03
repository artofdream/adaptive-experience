# Path B florist #384 — migration 023 applied; channel live (2026-09-03)

> **Tags**: #aea #path-b #florist #384 #migration-023 #channel #ecs
> **When**: 2026-09-03 ~07:22 Europe/Berlin
> **Related**: [[2026-09-03-path-b-florist-384-redeploy-prove]] · [[2026-09-02-florist-operator-session-facts-383-385]] · [[2026-09-02-native-web-florist-story-plain-language]]
> **Plain twin**: [[2026-09-03-florist-channel-web-live-plain-language]]

## Outcome

#384 close criteria met on live Path B (`https://aea.artof.link`):

| Check | Result |
|---|---|
| Migration 023 | Applied via ECS `RunTask` |
| `GET /api/v1/operator/orders` | **200** (was **500**) |
| Fresh web checkout `X-AEA-Client: web` | Order `cf5c26c2-2144-44fd-b213-727b19b4654a` shows **`channel=web`** on florist staff list |
| Pre-migration rows | `channel` null (expected) |
| Issue | Evidence comment posted on #384; **closing #384** |

## Migration apply (facts)

| Field | Value |
|---|---|
| When | 2026-09-03 ~07:22 Europe/Berlin |
| Cluster | `aea-pilot` |
| Task definition | `aea-pilot-orchestration` |
| Task id | `30569e8ea08541a0a23d27112dbbe97b` |
| Command | `python platform/scripts/apply_migrations.py` |
| Exit | **0** |
| CloudWatch | applied `023_order_operator_channel.sql`; SUMMARY **7 migrations applied** |
| SQL | `platform/migrations/023_order_operator_channel.sql` |

`deploy-ecs` still does **not** run migrations (known gap; same as [[2026-09-03-path-b-florist-384-redeploy-prove]]).

## AWS auth path used

- Applied via **cts-ai CLI** (IAM user `cts`, account `737290977112`).
- Cursor AWS MCP cannot interactive re-auth (`stdio_unsupported`) — so MCP was not the apply path this pass.

## Live prove (after migration)

| Check | Result |
|---|---|
| `GET /api/v1/operator/orders` | **200** (cleared the pre-023 500) |
| Session | `6d441af5-e157-41ff-bb3f-cff4923dd46d` |
| Fresh web order | `cf5c26c2-2144-44fd-b213-727b19b4654a` with `X-AEA-Client: web` → florist staff list **`channel=web`** |
| Older rows | `channel` null where order predated column (expected; not a regression) |

## Relation to prior note

Prior capture [[2026-09-03-path-b-florist-384-redeploy-prove]] documented the 500 + missing `orchestration.customer_order.aea_client` and the blocked AWS-MCP / waiting-pipeline unblock. This note records the successful apply + live channel proof and #384 close.

## Honesty

- Do not invent further deploys or native-channel proofs beyond the web checkout above.
- Pre-migration null channel is expected, not a bug.
- MRC merges this vault MR; do not self-merge.
