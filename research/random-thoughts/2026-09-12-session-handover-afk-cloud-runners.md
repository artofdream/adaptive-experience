# Session Handover: Sponsor AFK & Cloud Runner Autonomy (2026-09-12)

> **Tags**: #aea #second-brain #handover #session-memory #afk #cloud-autonomy #knowledge-first
> **Captured**: 2026-09-12 ~12:35 CEST (10:35 UTC) — Berlin late morning+
> **Author**: `@aea-knowledge-guardian` with `@aea-project-manager`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **GitLab**: [#429](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/429) (this vault MR) · do **not** close [#27](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/27) / [#35](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/35) / [#36](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/36)
> **Related**: [[2026-09-05-session-handover-cts-ai-afk-cloud-agents]] · [[2026-09-04-session-handover-afk-cts-ai]] · [[2026-09-03-session-handover-afk-cloud-runners]] · [[2026-09-12-session-memory-log-fr-016-ai-need-reminder-copy-425]] · [[2026-09-12-session-memory-log-fr-008-path-b-modify-before-reorder-424]] · [[2026-09-11-finops-414-arm-cutover-honesty]]

---

## 1. Why this note exists (plain)

The sponsor is **AFK for a few hours** on 2026-09-12 (Berlin morning into early afternoon). Local `cts-ai` is not the live bus. Cursor cloud agents, GitLab CI runners, and ECS `aea-pilot` keep going.

This node is the **shared memory** other agents must inherit. The DATE_RE brief `research/daily-briefs/2026-09-12.md` is **generator-owned** (`scripts/generate_daily_brief.py`). Do **not** hand-edit it for AFK. Knowledge First: write here, then let the next generator pass pick the note up.

Style inherits the 3 / 4 / 5 Sep AFK handovers — one issue, one branch, one MR, honest leftovers, named do-nots.

---

## 2. Verified live state (2026-09-12 ~10:35 UTC)

`origin/main` at vault write: `2167050` — `feat(path-b): FR-008 modify-before-reorder after Need Reorder (#424)`.

| Item | State |
|---|---|
| Open MRs | **None** (sponsor `artofdream` merged !504 at 10:29 UTC after CI green) |
| !503 / #425 | **Merged** 10:25 UTC — AI-authored Path B Need reminder copy. Parent **#35 stays open**. |
| !504 / #424 | **Merged** 10:29 UTC — modify-before-reorder after Need Reorder. Parent **#27 stays open**. Launched as in-flight; closed before this note was written. |
| #426 / #427 / #428 | **Opened + cloud agents launched** (RUNNING). No child MRs yet at this write. |
| #27 / #35 / #36 | **Opened** (workbook Future). Never close from a child MR. |
| Companion on `main` | `versionCode` **9** / `0.1.0-alpha.9` |
| Play | Do **not** change Play policy, bump `versionCode`, or treat App Dist as Play honesty |
| FinOps | Stay `us-east-1`. **No Savings Plan** before the **17 Sep** FinOps routine |
| DATE_RE bus | `research/daily-briefs/2026-09-12.md` (generated 04:09 UTC — **stale vs this morning's merges**; treat git/GitLab as SoT until the next generator run) |

Public runtimes (independent of `cts-ai`):

* Shop / operator: https://aea.artof.link (ECS Fargate `aea-pilot`)
* Architecture Pages: https://architecture.artof.link
* Grafana: https://aea.artof.link/grafana/

---

## 3. What shipped today (technical)

### 3.1 !503 / #425 — AI pull copy (merged)

Child of #35 / [[FR-016]]. Does **not** close #35. Does **not** reopen #420.

* `complete_chat_json` is the shared OpenAI-compatible helper.
* `OpenAICompatibleReminderCopyAuthor` + `AvailableReminderCopyAuthor` take only `occasion_type`, `recipient_relation`, `days_until_event`.
* `EngagementCrmService.get_reminders` authors the soonest item when a `copy_author` is wired; fail-closes to `format_reminder_text`.
* Same `AEA_AI_*` triple as intent. Still **pull-only**. No email / SMS / FCM / APNs.
* Image-scan unblock: orchestration rebuilds digest-pinned `libpcre2-8-0` (do not widen `image-scan-exceptions.json`).

Honest leftover on #35: unsolicited **outbound send**. Vault: [[2026-09-12-session-memory-log-fr-016-ai-need-reminder-copy-425]].

### 3.2 !504 / #424 — modify-before-reorder (merged)

Child of #27 / [[FR-008]]. Does **not** close #27. Does **not** reopen #419 / #422.

* Live Path B reads size / quantity / card from the real `customer_order.product` snapshot (same-session accepted order or durable migration-017 `order_id` join).
* Options are **not** copied onto `browser_order_recall` and **not** served from the in-memory `ReorderService` store. `least_data_reorder_options` is the live equivalent.
* `#need-reorder` keeps **Reorder →** and adds sibling **Modify →**. Both land on existing T-04. #422 hide gates stay.
* Walker `walk_returning_shopper.py --payment` classifies modified Deluxe / qty / card into `selection`.

Honest leftover on #27: **multi-order purchase-history** chooser (that is #426). Vault: [[2026-09-12-session-memory-log-fr-008-path-b-modify-before-reorder-424]].

---

## 4. Launched children (one issue → one MR)

Cloud agents were started 2026-09-12 ~10:27 UTC. At this write they are **RUNNING** with **no branch / no MR** yet. Do not steal the issue if that agent is still live. If it dies, take **one** row from updated `origin/main`.

| # | Parent | Slice | Cloud agent | Hard stop |
|---|---|---|---|---|
| **#426** | #27 / FR-008 | Path B multi-order prior SKU history chooser (least-data `prior_orders[]`, last 3–5, #422 hide gates) | [AEA #426](https://cursor.com/agents/bc-f4ba2db5-a1b9-53ed-a409-987ef7365f4e) | Never `Closes #27`. No login / CRM accounts. |
| **#427** | #36 / FR-017 | Florist zero-PII engagement **cohort export** (CSV/JSON of counts + categorical keys only) | [AEA #427](https://cursor.com/agents/bc-98197870-3582-56b5-8fd6-5c0e4e973e6e) | Never `Closes #36`. No per-customer list / ML. |
| **#428** | #35 / FR-016 | Outbound reminder **outbox dry-run** (`status=dry_run` / `not_sent`; send stub fail-closed) | [AEA #428](https://cursor.com/agents/bc-0c35f1e2-8384-5784-81fe-685e78abe7d2) | **No live email / SMS / SES / SMTP / SendGrid.** No FCM/APNs. Never `Closes #35`. |

This vault agent: [AEA AFK vault handover 12 Sep](https://cursor.com/agents/bc-ce5a5d7f-6c0c-5021-bd8f-94211ae8cda7) → #429 only.

If a child MR's `Closes` token **auto-closes** #27, #35, or #36: **reopen the parent immediately** and comment that the close was a token accident. Child issues may close. Parents must not.

---

## 5. Do not process while the sponsor is AFK

| Item | Why it is reserved |
|---|---|
| **AWS Compute Savings Plan** | Re-eval is the **17 Sep FinOps routine**. Prior tiny `$0.04/hr` SPs are retired. Do not purchase from #414 / #415 leftovers or this window. [[2026-09-10-finops-414-partial-apply-honesty]] · [[2026-09-10-finops-414-rds-arm64-apply-continuity]] |
| **Play policy / Play Console** | No policy edits, no `versionCode` 10, no new AAB, no treating App Dist as Play honesty. Companion on `main` is already v9. |
| **Live email for #428** | Outbox dry-run only. No sanctioned Path B SES/SMTP. ADR-019 push stays a decision record. |
| **Closing #27 / #35 / #36** | Workbook Future. Child slices only. Reopen if GitLab auto-closes on `Closes`. |
| **`terraform apply` / new secrets / KMS / region move** | Sponsor. Stay `us-east-1`. Keep MSK. ARM64 cutover already live on cts-ai — [[2026-09-11-finops-414-arm-cutover-honesty]]. |
| **Hand-edit DATE_RE brief** | Generator-owned. This handover is the AFK bus. |
| **Native florist / operator Android** | Not requested. Operator stays `/florist` mobile-web. |
| **Inbox `*.mp4`** | Evidence only; do not commit. |
| **Invent FR/NFR IDs** | Archive xlsx is SoT. |

---

## 6. Cloud agent / runner playbook

1. `git fetch origin && git checkout main && git pull --ff-only origin main`.
2. Read **this file** + the latest DATE_RE brief + the **one** issue you own.
3. If #426 / #427 / #428 already has a live cloud agent or open MR, **do not double-start**.
4. Branch from updated `main`. Docs-only → no Docker. Platform/edge → local Compose recipe if Docker exists; otherwise say skipped (prefer wait over silent CI-only unless PM already accepted CI-only for that named MR).
5. `python scripts/run_all_guards.py` (14/14).
6. MR body: `## Validation:` + exactly one closing issue (`Closes #426` / `#427` / `#428` / `#429`). **Never** `Closes #27` / `#35` / `#36`.
7. Author posts an MRC create/push note (`--resolvable=false`). **Stop.** Do not start the next child in the same MR.

GitLab CI and ECS `aea-pilot` keep running without `cts-ai`.

---

## 7. MRC (this window)

`@aea-mr-coordinator` **merges green non-draft MRs** when scope, boundary, and validation pass (`glab mr merge <n> --yes --auto-merge` / MWPS). Do not wait for a second named-MR prompt.

* !504 was green + mergeable; sponsor merged it directly at 10:29 UTC. That is done — do not reopen #424.
* The next green non-draft child / this #429 docs MR should be gated and auto-merged the same way.
* Required job red → request `@aea-senior-software-engineer` (or `@aea-devsecops-platform` for runner / image / compose). Do not sit on a red job. Do not rebase from MRC.

---

## 8. Resume when the sponsor is back

1. `git pull --ff-only origin main`.
2. `glab mr list` / `glab issue list` — expect #426 / #427 / #428 movement; #27 / #35 / #36 still open.
3. If a parent was auto-closed by a `Closes` token, reopen it before anything else.
4. FinOps Savings Plan stays parked until the **17 Sep** routine — not “later today”.
5. Next generator run: `python scripts/generate_daily_brief.py` (do not hand-patch `2026-09-12.md` from memory).

---

## 9. Wikilinks

[[2026-09-05-session-handover-cts-ai-afk-cloud-agents]] · [[2026-09-04-session-handover-afk-cts-ai]] · [[2026-09-03-session-handover-afk-cloud-runners]] · [[2026-09-02-session-handover-cloud-agents-local-cts-ai]] · [[2026-09-12-session-memory-log-fr-016-ai-need-reminder-copy-425]] · [[2026-09-12-session-memory-log-fr-008-path-b-modify-before-reorder-424]] · [[2026-09-11-session-memory-log-fr-016-path-b-need-reminder-420]] · [[2026-09-11-session-memory-log-fr-017-florist-engagement-421]] · [[2026-09-11-session-memory-log-need-reorder-visibility-422]] · [[2026-09-11-finops-414-arm-cutover-honesty]] · [[2026-09-10-finops-414-partial-apply-honesty]] · [[2026-09-10-finops-414-rds-arm64-apply-continuity]] · [[ADR-016]] · [[ADR-019]] · [[ADR-020]] · [[FR-008]] · [[FR-016]] · [[FR-017]]
