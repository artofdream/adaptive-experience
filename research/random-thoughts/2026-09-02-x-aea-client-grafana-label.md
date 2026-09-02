# X-AEA-Client / `aea_client` operator label (#368)

> **Tags**: #aea #companion #grafana #observability #gap-loop #honesty
> **Captured**: 2026-09-02
> **Updated**: 2026-09-02 (as-code request panels)
> **Issue**: [#368](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/368)
> **Related**: [[2026-09-02-companion-native-web-gap-closing-loop]]

## What landed

| Emitter | Header value |
|---------|----------------|
| Android `BffClient` | `X-AEA-Client: companion-android` |
| Web `app.js` / `florist.js` | `X-AEA-Client: web` |

Edge nginx (`nginx.conf` / `nginx-alb.conf`): forwards `X-AEA-Client` on `/api/`; access log field `aea_client="$http_x_aea_client"`.

BFF (`edge/bff/aea_bff/app.py`): allowlist `companion-android` | `web` (else metrics label `unknown`); echo response header; JSON stdout event `bff_access` with field **`aea_client`** (`unspecified` if absent). **Not used for auth.**

## Operator query (CloudWatch Logs Insights)

Log group: **`/aea/aea-pilot/bff`** (region `us-east-1`).

Label name:

```
aea_client
```

Count by client × status:

```
fields @timestamp, aea_client, status, path, method
| filter event = "bff_access"
| stats count(*) as requests by aea_client, status
```

Request series (5m bins — matches Grafana panel):

```
filter event = "bff_access"
| stats count(*) as requests by aea_client, bin(@timestamp, 5m)
```

Nginx gateway stdout (`/aea/aea-pilot/gateway`) also carries `aea_client="…"` on the `aea_edge` log format (string field, not JSON `event`).

## Grafana as-code panel path

Dashboard uid **`aea-unified-dashboard`**  
File: `platform/docker/grafana/provisioning/dashboards/aea_unified_dashboard.json`  
Staging UI: `https://aea.artof.link/grafana/` (home dashboard).

| Panel | Type | Query |
|-------|------|-------|
| **BFF requests by aea_client (X-AEA-Client)** | timeseries | Logs Insights on `/aea/aea-pilot/bff`, `stats count(*) by aea_client, bin(@timestamp, 5m)` |
| **BFF aea_client × status (table)** | table | same log group, `stats count(*) by aea_client, status` |

Datasource: CloudWatch uid `cloudwatch`, `queryMode: Logs`, region `us-east-1`.

## Verify after edge / Grafana deploy

1. **Edge + BFF** tasks running a build that includes !388 (`X-AEA-Client` forward + `bff_access.aea_client`). Force new deployment if needed:
   `aws ecs update-service --cluster aea-pilot --service bff --force-new-deployment`
   (and `gateway` if nginx log field is required).
2. **Grafana** image/provisioning refresh so file dashboards pick up panel ids 20/21 (ECS grafana service redeploy or wait for `updateIntervalSeconds: 30` if volume-mounted; container image rebuild if JSON is baked into the image).
3. Generate mixed traffic: one companion (or `scripts/probe_companion_bff_parity.py`) path and one browser shop hit.
4. CloudWatch Logs Insights on `/aea/aea-pilot/bff` — expect `companion-android` and/or `web` rows (not only `unspecified`).
5. Grafana Explore or the two panels above — series/table populate. Empty panels ⇒ check log group ARN, IAM `logs:*`, and that JSON lines actually contain `"event": "bff_access"`.

Honesty: **query documented / panel as-code**. Live native-vs-web series are **not** claimed until steps 3–5 succeed on staging.

## Out of scope (still)

Separate Bearer tokens; Play; device farm; using `X-AEA-Client` as a security boundary; executive dashboard client panels.
