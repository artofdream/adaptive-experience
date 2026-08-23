# !259 + graph-loop: 24h validation soak

tags: #aea #inbox #process
status: inbox
captured: 2026-08-20
updated: 2026-08-21

## Note

Sponsor moved the 24h hold: it started **2026-08-19 14:00 Europe/Paris**
(`2026-08-19T12:00:00Z`), not last night. Evaluated **2026-08-20 ~14:25
Europe/Paris** (`~2026-08-20T12:25:00Z`). Elapsed ~24h 21m.

## Telemetry verdict: **enough**

Path B `https://aea.artof.link/` (account `737290977112`, `us-east-1`,
cluster `aea-pilot`) has a 24h ALB + CloudWatch trail, not a single 200.

- `GET /healthz` → 200 `{"status":"ok"}` (nginx + BFF). ALB target 2xx
  present in every hour from 19 Aug 14:00 Paris through 20 Aug 14:00 Paris.
- `GET /cloud/status` → 200
  `autonomous_loop_enabled:true`, `cluster:aea-pilot`,
  `service:aea-agent-runner`, `status:active`.
- `GET /webhooks/` → 404 FastAPI `{"detail":"Not Found"}` (no GET route on
  that path). `GET /webhooks/gitlab` → **405** `allow: POST` as expected.
  Do not forge webhook payloads.
- ALB `aea-pilot-alb`: hourly RequestCount across the window. Target 5xx
  only in the 19 Aug 20:00 Paris hour (13 target + 7 ELB 5xx) during
  agent-runner first boot. Otherwise 2xx-only hours.
- ECS: `gateway` 1/1 (older task still serving). `agent-runner` 1/1 since
  19 Aug 20:31 Paris (created 19:40; not up at hold start). Secret
  `aea/gitlab-token` exists (name only; value not read).
- GitLab is already POSTing `/webhooks/gitlab` (200, 133-byte stub body).

## !259 merge status: **already merged** — do not re-merge

- Merged `2026-08-19T22:18:27Z` (`8de13a1`), HEAD of the MR was `1d291b6`.
- Pipeline 909 **success with warnings** (advisory lint/traceability;
  blocking `edge-docker-integration` green). Auto-merge had been cancelled
  earlier; merge still landed.
- Live Path B **does** have !259 routes (`/webhooks/`, `/cloud/`). Soak
  was ~8h pre-merge + ~14h post-merge of !259, then later `e50b447`
  (cart + Grafana leftovers) landed on `main`.

## Live incident (after soak, during this pass)

`e50b447` committed **unresolved conflict markers** in
`edge/gateway/nginx-alb.conf`. New gateway tasks crash:

```
nginx: [emerg] unknown directive "<<<<<<<" in /etc/nginx/nginx.conf:64
```

PRIMARY rollout failed (exit 1). Old task still serves. **Next slice is
this nginx syntax fix**, not Grafana leftovers and not a closed-loop
merge runner. Grafana public `/grafana/` stays out of the nginx-fix MR.

## Graph-loop / agent-runner: **hollow stub** (working HTTP, not a loop)

- FastAPI serves `/cloud/status` and POST `/webhooks/gitlab`.
- `process_gitlab_webhook` / `trigger_autonomous_remediation` return
  dicts only — no `glab` / GitLab API call despite `aea/gitlab-token`.
- `/cloud/status` is an env-flag echo, not ECS health.
- First boot 19 Aug ~20:02 Paris: `ModuleNotFoundError:
  No module named 'platform.aea_platform'` then `Attribute "app" not
  found`; recovered ~20:28 (`Application startup complete`). Current
  Dockerfile CMD is `aea_platform.agent_gateway:app`.

**Follow-up slice (separate issue/MR after nginx fix):** make POST
`/webhooks/gitlab` actually use the existing secret (acknowledge vs
draft-only; **no unattended merge**). Do not batch with Grafana.

## Merge / no-merge this pass

- !259: **already on main**. MRC gates would have passed (scope/boundary
  / pipeline 909 required jobs green). Nothing to merge.
- Nginx-fix: issue #252,
  [!263](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/263)
  (`4b9e0b6`). Local edge Docker integration passed. **Not** auto-merged
  from this soak tick — wait for blocking CI on !263.

## Sponsor ask

**None.** `aea/gitlab-token` already exists in Secrets Manager. No
tfvars/.env paste, no destroy, no GITLAB_TOKEN paste required to finish
telemetry or the nginx syntax fix.

## Sleeper aborted (2026-08-21 ~15:06 Europe/Paris)

The original one-shot `Start-Sleep 86400` (PID 34200, sentinel
`AGENT_LOOP_WAKE_mr259_graph_soak`) **aborted** and never emitted the
wake. Soak had already been evaluated on 20 Aug (above). Recheck now:

- Live `GET /cloud/status` → 200 same stub JSON (`status:active`,
  `autonomous_loop_enabled:true`). Still an env-flag echo, not a loop.
- Live `GET /webhooks/` → 404; `GET /webhooks/gitlab` → 405 `POST` only.
- !259 and nginx-fix !263 are **both merged**. Do not re-merge. Do not
  re-arm a 24h sleeper.

## Links

- Related docs: `research/loop-graph.md`,
  `docs/04-technical-architecture/autonomous-cloud-agent-sop.md`
- MR: https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/259
- Live: https://aea.artof.link/healthz
