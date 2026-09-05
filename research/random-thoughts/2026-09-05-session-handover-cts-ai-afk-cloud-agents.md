# Session Handover: cts-ai AFK — cloud agents / runners / instances (2026-09-05)

> **Tags**: #aea #second-brain #handover #session-memory #cts-ai #afk #cloud-autonomy
> **Captured**: 2026-09-05 ~17:00 CEST
> **Author**: `@aea-project-manager` with `@aea-knowledge-guardian`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[2026-09-05-session-memory-log-a36-play-v8-honesty-401-402]] · [[2026-09-05-session-memory-log-rog-play-v8-404-absent]] · [[2026-09-04-session-handover-afk-cts-ai]] · [[2026-09-04-future-native-florist-operator-app-gates]] · [[2026-09-03-session-handover-afk-cloud-runners]]

---

## 1. Why this note exists

Local workstation **`cts-ai`** is focusing on **another project for the next hours**. This is the durable handoff for Cursor **cloud agents**, GitLab **CI runners**, and AWS **ECS instances**. Do not wait on `cts-ai` ADB, Docker Desktop, or the sponsor daily phone.

Live DATE_RE bus: `research/daily-briefs/2026-09-05.md` (ignore `*-daily-brief.md` / uncommitted `*-activity-report.md`).

---

## 2. Verified live state (2026-09-05 ~16:10 UTC)

| Item | State |
|---|---|
| `origin/main` HEAD at handoff write | `3ee4191f0686` — Merge !465 A36 Play v8 honesty |
| Open MRs | **None** (MRC **bench**) |
| Companion on `main` | `versionCode` **8** / `0.1.0-alpha.8` |
| Play Internal | **v8 already used** (2026-09-05 web pipeline [2822802127](https://gitlab.com/artof-group/adaptive-experience-architecture/-/pipelines/2822802127): bundle [16324668240](https://gitlab.com/artof-group/adaptive-experience-architecture/-/jobs/16324668240) success; Play upload [16324668241](https://gitlab.com/artof-group/adaptive-experience-architecture/-/jobs/16324668241) failed honestly `Version code 8 has already been used.`) |
| Operator native app | **Do not start.** Sponsor: no operator native unless specifically requested. Gates: [[2026-09-04-future-native-florist-operator-app-gates]] |
| Operator surface | Mobile-web `/florist` only. Figma node IDs on `main` via !464 |
| #398 / #352 / #401 / #402 / #404 / #405 | **Closed** on GitLab. #404 Play tap remains **Unknown** on A36 **and** ROG Play v8 (CTA **ABSENT**). Follow-up **#407** — do not reopen #404 |
| CF queue active | **CF-054** `regressed` (clip after CSS Unknown). **CF-056** still `in-mr` in the queue though !361 **merged** 2026-08-31 — honesty drift |

Public runtimes (independent of `cts-ai`):

* Shop / operator: https://aea.artof.link (ECS Fargate `aea-pilot`)
* Architecture Pages: https://architecture.artof.link
* Grafana: https://aea.artof.link/grafana/

---

## 3. Actionable now (cloud-safe) — process in this order

One issue → one branch from **updated `origin/main`** → one MR. Author posts MRC create/push note. **Do not merge** unless `@aea-mr-coordinator` is invoked. Serialize `.gitlab-ci.yml`. Do not invent FR/NFR IDs. Do not commit secrets, inbox `*.mp4`, or Android `app/build`.

### P0 — do first

| # | Owner | Why it is unblocked | Do |
|---|---|---|---|
| **#323** | `@aea-coherence-guardian` + `@aea-devsecops-platform` | !341 **merged**. `#324` waits on this. Both touch `.gitlab-ci.yml`. | Establish a **clean traceability baseline**, then remove `allow_failure` / shell suppression on `traceability-guard` only. Prove direct checker + tests + `run_verify_job`. Required job green. **Stop.** Do not start #324 in the same MR. |

### P1 — after #323 merges (not before)

| # | Owner | Gate |
|---|---|---|
| **#324** | PM policy + coherence + DSO | After the #323 MR is on `main` |
| **#325** then **#326** | Knowledge + DSO | After #324. Pin lint/link tools; prove a negative fixture fails; then make the job required |
| **#327** | SSE + DSO | After compile gate (already required). **Serialize `.gitlab-ci.yml`** — do not collide with #323–#326 |
| **#328** | AppSec policy + SSE + DSO | After Ruff baseline; not the same MR as SCA |
| **#329** then **#330** | SSE then AppSec/SCA | Locks before vulnerability scanning |
| **#331** then **#332** | DSO | Digest pin before image scan/SBOM. Existing AWS OIDC only |
| **#334** | DSO + AppSec | After formatting cleanup; serialize `.gitlab-ci.yml` |

Local `cts-ai` had a **checkout named** `quality/327-blocking-ruff-baseline` with **no commits** and a dirty Ruff `--fix` tree that was **restored**. Cloud **may** take #327 only after #323 (and preferably #324–#326) land. Do not resume that leftover local dirty tree.

### P1b — queue honesty (parallel with #323; different files)

| ID | Owner | Do |
|---|---|---|
| **CF-056** | `@aea-coherence-guardian` | !361 already merged (`#342`). Confirm `docs/framework/comparison.md` + `journal.md` + glossary Probe example cross-link. If true: one docs MR to set queue row 56 + `research/findings/CF-056-daily-brief-honesty-claim-vs-probe.md` to `verified`. If the cross-link is missing, fix **only** that claim. **Do not** restyle Path B. **Do not** mark CF-054 verified. |

---

## 4. Do not process while cts-ai is away

| Item | Why it is reserved |
|---|---|
| **Native florist / operator Android** | Sponsor: not requested. Four gates still closed |
| **CF-054** Path B dual-viewport `verified` | Needs phone **and** desktop journey clips **dated after** CSS !300. Cloud cannot mint those clips honestly |
| **#404 / #407 Play reorder-tap** | ROG Play v8 cold-start Need also **ABSENT** (same as A36). Do **not** sideload debug over A36. Play-honest wallet dump / Confirm→Start Over is #407 |
| **Play `versionCode` 9** / new AAB | Not requested. v8 is already on Internal |
| **Firebase App Dist** | Optional; not Play honesty |
| **#27 / #35 / #36** and epics #13–#19 | Workbook **Future**. Need `@aea-product-owner` unpark (M12 still parked) |
| **PWA / Add-to-Home-Screen** | After operator-native gates doc; not this AFK window |
| **`terraform apply` / new secrets / KMS** | Sponsor |
| **Inbox `*.mp4`** | Evidence only; do not commit |

---

## 5. Cloud agent / runner playbook

1. `git fetch origin && git checkout main && git pull --ff-only origin main`.
2. Read this file + `research/daily-briefs/2026-09-05.md` + the issue body you own.
3. Take **one** P0/P1b row. Comment on the GitLab issue that a cloud agent claimed it (HEAD SHA + branch name).
4. Branch `quality/323-blocking-traceability-gate` or `docs/cf056-queue-verified` from updated `main`.
5. Docs-only → no Docker. CI / platform / edge → run the matching local recipe **if the cloud VM has Docker**; otherwise say skipped and wait (PM prefers wait over silent CI-only).
6. `python scripts/run_all_guards.py` (14/14).
7. `glab mr create` with `Closes #N` when the issue should close. Then MRC create note (`--resolvable=false`).
8. Stop. Do not start the next DSO number in the same MR.

GitLab CI and ECS `aea-pilot` keep running without `cts-ai`. Do not play Android signed jobs unless a new companion `versionCode` lands (it should not, this window).

---

## 6. Resume on cts-ai (later)

1. `git pull --ff-only origin main`.
2. `glab mr list` / `glab issue list`.
3. If #323 merged, the next human or cloud slice is **#324**, not #327.
4. Hardware: A36 = Play companion only. ROG = debug / #404 tap prove. Do not mix.
