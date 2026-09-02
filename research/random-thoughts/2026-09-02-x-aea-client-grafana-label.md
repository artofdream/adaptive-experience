# X-AEA-Client / `aea_client` operator label (#368)

> **Tags**: #aea #companion #grafana #observability #gap-loop #honesty
> **Captured**: 2026-09-02
> **Issue**: [#368](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/368)
> **Related**: [[2026-09-02-companion-native-web-gap-closing-loop]]

## What landed

| Emitter | Header value |
|---------|----------------|
| Android `BffClient` | `X-AEA-Client: companion-android` |
| Web `app.js` / `florist.js` | `X-AEA-Client: web` |

Edge nginx (`nginx.conf` / `nginx-alb.conf`): forwards `X-AEA-Client` on `/api/`; access log field `aea_client="$http_x_aea_client"`.

BFF (`edge/bff/aea_bff/app.py`): allowlist `companion-android` | `web` (else metrics label `unknown`); echo response header; JSON stdout event `bff_access` with field **`aea_client`** (`unspecified` if absent). **Not used for auth.**

## Operator query

CloudWatch Logs Insights (BFF task logs), label name:

```
aea_client
```

Example:

```
fields @timestamp, aea_client, status, path, method
| filter event = "bff_access"
| stats count(*) as requests by aea_client, status
```

Nginx gateway stdout also carries `aea_client="…"` on the `aea_edge` log format.

## Grafana honesty

Repo dashboards under `platform/docker/grafana/provisioning/dashboards/` are CloudWatch **infra** (CPU/mem/tasks). No as-code request-series panel for client channel yet → status **partial**. Do not claim staging Grafana panels show native vs web series until an Explore/Logs panel or dashboard JSON is added and probed.

## Out of scope (still)

Separate Bearer tokens; #369 weekday probe; Play; device farm; using `X-AEA-Client` as a security boundary.
