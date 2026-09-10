# FinOps: CloudWatch metric prune for Grafana (keep dashboards)

> **Tags**: #aea #second-brain #finops #cloudwatch #grafana #cost-guardian
> **Captured**: 2026-09-10
> **GitLab**: #414
> **Owners to inherit**: @aea-cost-guardian, @aea-devsecops-platform

## What the bill actually is

Pilot CloudWatch spend is almost entirely `CW:MetricMonitorUsage`
(~$30/mo), not log storage. ECS log groups already had
`retention_in_days = 30`; #414 drops that to **14 days** as a
secondary cut. Grafana Logs Insights panels on
`/aea/aea-pilot/bff` (`aea_client` series) still work at 14 days.

## Do not break Grafana

Provisioned dashboards query **`AWS/ECS`** (CPU/memory per service) plus
CloudWatch **Logs** Insights. They do **not** need a second custom
metric namespace that duplicates those series.

- Keep `AWS/ECS` metrics Grafana already scrapes. Do not delete those
  namespaces or IAM `CloudWatchReadOnlyAccess`.
- Do **not** `PutMetricData` the same CPU/memory series into a custom
  namespace while Grafana reads CloudWatch. Dual-shipping is what
  inflates `MetricMonitorUsage`.
- Cut unused **custom** metrics (idle `PutMetricData` names, leftover
  test namespaces). Do not remove panels or change datasource UIDs.
- Cluster `containerInsights = enabled` publishes a large custom set
  (`ECS/ContainerInsights`). Dashboards today use `AWS/ECS`, not that
  namespace. DSO may disable Insights **after** confirming no live
  panel depends on it. This MR does **not** flip that setting.

Existing IDs: [[2026-08-29-finops-arm64-and-rds-sizing]], [[2026-08-29-finops-cost-optimization-rationale-and-enforcement]], [[2026-08-22-cloud-grafana-cloudwatch-troubleshooting-sop]], [[2026-09-02-x-aea-client-grafana-label]], [[2026-09-10-finops-414-partial-apply-honesty]].
