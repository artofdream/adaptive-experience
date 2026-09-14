# Session Memory Log: migrate-on-deploy LIVE prove (#436 / #438 chain, 2026-09-14)

> **Tags**: #aea #session-memory #deploy #migrations #iam #honesty #path-b #second-brain #keep-learning-and-apply
> **Captured**: 2026-09-14
> **Author**: `@aea-knowledge-guardian` with `@aea-devsecops-platform`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **GitLab**: [#440](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/440) (this vault MR) · related merged [!517](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/517) / [#438](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/438) · chain [#436](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/436) / [#437](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/437)
> **Related**: [[2026-09-12-session-memory-log-deploy-ecs-apply-migrations]] · [[2026-09-13-session-memory-log-deploy-ecs-runtask-accessdenied]] · [[2026-09-14-session-memory-log-deploy-ecs-describetasks-accessdenied]]
> **This node is knowledge.** It records a live CI prove. It does not reopen product tickets.

---

## 1. Claim (falsifiable)

**migrate-on-deploy Prove** for the **#436 / #438** chain on Path B `aea-pilot`: after !517 IAM (`ecs:DescribeTasks` + `ecs:ListTasks` on `EcsDeployUntaggedRegister`), main `(aws) deploy-ecs` ran migrations in-pipeline and reached healthy `/healthz`.

## 2. Evidence (this session)

| Fact | Value |
|---|---|
| MR | [!517](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/517) **merged** (IAM DescribeTasks + ListTasks) |
| Job | [`deploy-ecs` 16488714090](https://gitlab.com/artof-group/adaptive-experience-architecture/-/jobs/16488714090) |
| Status | **SUCCESS** |
| Finished | `2026-09-14T14:36:48Z` |
| Migrate log | `ecs_apply_migrations: OK` — task `0a419082d9924c73ad35e1c0bd439df0` **exitCode=0** |
| Health | `/healthz` → `{"status":"ok"}` |

Prior honesty: #436 wired migrate into `deploy-ecs`; #437 fixed `ecs:RunTask` AccessDenied; #438 / !517 fixed waiter `ecs:DescribeTasks` AccessDenied. Until this green job, live migrate-on-deploy remained Unknown/failed in vault notes.

## 3. Tracker honesty

- !517 already merged and closed #438. This vault MR closes **#440 only**.
- Do **not** `Closes #436` / `Closes #437` / `Closes #438` from this note.
- One green job is the prove for that pipeline SHA/time; future deploys can still fail for other reasons — do not over-claim forever-green.

## 4. Wikilinks

[[2026-09-12-session-memory-log-deploy-ecs-apply-migrations]] · [[2026-09-13-session-memory-log-deploy-ecs-runtask-accessdenied]] · [[2026-09-14-session-memory-log-deploy-ecs-describetasks-accessdenied]] · [[2026-09-14-session-memory-log-path-b-dual-viewport-probe]]
