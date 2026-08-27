# Honesty crisis covering node (2026-08-23 through 2026-08-27)

> **Tags**: #aea #second-brain #honesty #knowledge-first #coherence #antifragility #path-b
> **Captured**: 2026-08-27
> **GitLab**: #271
> **Related**: #257, #259 / !280 (CF-048), #270 (open), #265 / !290, #268 / !289, #269 / !291
> **Owners to inherit**: @aea-knowledge-guardian, @aea-coherence-guardian, @aea-ai-engineer, @aea-devsecops-platform, @aea-mr-coordinator, @aea-project-manager
> **This node is knowledge, not a merge of product work.**
> **Probed**: `origin/main` @ `8c39635`, `glab issue list` (15 open), `glab mr list` (0 open), 2026-08-27 evening.

Later agents: do not rediscover this from chat. Shared memory is committed GitLab `main` only. A status word is a claim. Probe in the same session or write Unknown.

Inherits [[2026-08-25-trust-but-verify-job-and-single-role-list]] and [[2026-08-26-date-re-bus-and-agent-runner-image-roll]]. Origin assessment: Grok CF-048 intake under `research/grok-branch/` (not a vault wikilink target).

---

## 1. What the crisis was

The dominant failure class from 2026-08-23 was **delivery-claim honesty**, not missing product code. Publishers (daily brief generator, roadmap Completed tags, always-loaded role counts, session-memory logs) printed Completed / ACTIVE / shipped without a mechanical evidence path. Regeneration overwrote honest hand-edits. Uncommitted DATE_RE files were treated as the bus; other machines and tools never saw them.

Principle (sponsor, 2026-08-25): **what is written must match what is implemented. Trust but verify.** Hardcoded narrative is not evidence. Anti-fragility fails if the guard network believes its own press release.

Do **not** add a 15th stakeholder hat. Fourteen hats stay lenses. Three executable jobs: implement, verify (still missing as a job — #257 open), merge (MRC only).

---

## 2. Timeline (probed; do not reopen as new tickets)

| When | What actually landed on `main` | Tracker |
|---|---|---|
| 2026-08-23 | Assessment intake CF-048…053. Audit script TTFB relabel (script only). | CF-048 later #259; CF-049 loop still `queued` |
| 2026-08-25 | Knowledge node: verify job + single role-list. Did **not** implement the job. | #257 **open** |
| 2026-08-26 | Generator honest enough to drop 15/16 and M15 SSR/sub-100ms shipped claims. Canonical DATE_RE is `YYYY-MM-DD.md`. | #259 / !280 — CF-048 `verified` |
| 2026-08-26 | Always-loaded role count aligned to 14. | #262 / !284 |
| 2026-08-26 | Cadence / activity recap writes `research/random-thoughts/YYYY-MM-DD-daily-activity.md` only. Must not create/edit/restore DATE_RE. If git/glab/shell is down: write nothing. | #263 / !285 |
| 2026-08-26 | CI jobs to bake ECS `agent-runner`. Image is `COPY . .` — no git pull. | #264 / !286 |
| 2026-08-26 | OIDC `EcrPush` on `aea-pilot/agent-runner`. | #266 / !287 |
| 2026-08-26 | This DATE_RE vs runner lesson node. | #267 / !288 |
| 2026-08-27 | Shop `app.js` SyntaxError: unused live-chat stub broke parse; T-01 Send never reached the API. | #268 / !289 |
| 2026-08-27 | LiteLLM `400` `No connected db`. `edge/litellm.yaml` `master_key` + `allow_requests_on_db_unavailable: true`. Yaml rolls via Terraform/task, **not** `deploy-ecs`. | #265 / !290 |
| 2026-08-27 | Antigravity Always On: `.agents/rules/aea.md` Knowledge First + `glab issue list` before create. | #260 / !293 |
| 2026-08-27 | Scheduled `daily-brief-generate` commits DATE_RE (`scripts/commit_daily_brief.py`, CI only, `[skip ci]`). `STALE_AFTER_DAYS = 0`. Job-token push allowed. Proven pipeline 1070. | #269 / !291 |

Do not reopen any closed row as a new CF. Do not batch CF-049–053 into #257.

---

## 3. Path B diagnostic chain (T-01 did not update)

Live origin `https://aea.artof.link`. The first hypothesis (LiteLLM down) was wrong. Failures stacked; each fix unmasked the next. One finding → one issue → one MR at each layer.

```text
T-01 Send appears dead
        │
        ▼
#268  app.js SyntaxError (template-literal stub + fetch(/api/...))
        │  typeof boot === 'function' after merge
        ▼
#265  LiteLLM 400 No connected db (Prisma-less Path B)
        │  HEALTHY after yaml in task (aea-pilot-litellm:3)
        ▼
#270  litellm.Timeout ~2.048s on claude-sonnet-5 (Timeout passed=2.0)
        │  OPEN as of this capture
        ▼
      ReferenceIntentInterpreter fallback can still advance (sponsor saw T-04).
      Desired: 200 within the agreed budget, not timeout-only fallback.
```

Caps on `main` @ `8c39635`: `edge/litellm.yaml` `request_timeout: 2`; `AEA_AI_TIMEOUT` default `2.0`; `OpenAICompatibleIntentInterpreter` rejects `timeout_seconds > 2.5`. [[NFR-003]] is **availability via fallback**, not a mandate to wait 2.5s for Anthropic — the 2.5s ceiling exists so a slow provider fails closed to `ReferenceIntentInterpreter`. Do **not** blindly raise either cap. Owners: `@aea-ai-engineer` + `@aea-devsecops-platform`. One MR. Out of scope: #265, UX restyle, Antigravity enablement.

`deploy-ecs` still rolls `orchestration bff gateway relay consumer-workspace` — **not** `litellm`. LiteLLM changes need Terraform/task + force-deploy. Do not reuse #270 or #266 for that DSO slice.

---

## 4. DATE_RE, hats, and the generator leftover

Canonical session-start bus: committed `research/daily-briefs/YYYY-MM-DD.md`. Freshness `DATE_RE` is `^(\d{4}-\d{2}-\d{2})\.md$`. Historical `*-daily-brief.md` is not live. An uncommitted brief is not shared memory (four briefs in mid-August existed only on one laptop).

Owner: `scripts/generate_daily_brief.py` plus honest hand-review, or the **scheduled** CI job (`CI_PIPELINE_SOURCE == schedule`, play schedule `4394324`, cron `0 4 * * *` UTC). Playing the schedule also runs shop `build-ecr` / `deploy-ecs`. Cadence must not write DATE_RE (#263). This Grok session must not ritual-regenerate DATE_RE.

**Leftover (not a new CF):** the generator still hardcodes all 14 hats as `` `ACTIVE` `` in section 4. That reprint is **not** live team status. Honest matrix on 2026-08-27 evening: do now #270; then #257 verify job; then CF-049; MRC on the bench (0 open MRs). Track the leftover on #257; do not silently retitle #257 as CF-049.

---

## 5. Antigravity vs ECS `agent-runner`

| Writer | Writes DATE_RE? | Live role |
|---|---|---|
| Scheduled `daily-brief-generate` + `commit_daily_brief.py` | yes, CI only | Owner path after #269 |
| `@aea-coherence-guardian` cadence | no | Sidecar in random-thoughts |
| Antigravity Always On | no | Session-start SOP; `glab issue list` before create; does not merge |
| ECS `agent-runner` | no | HTTP stub + baked guards; `AEA_AUTONOMOUS_LOOP_ENABLED=true` pauses; does not pull git; not a second AGY |
| Generator hat matrix | reprints ACTIVE | Not a probe |

---

## 6. MRC merge pattern (inherit; this node does not merge)

Invoked MRC on **named** MRs only. Gates: one finding, diff matches, no secrets, Docker SOP or docs/IAM-only, required CI green or MWPS. Advisory fails (`markdownlint`, `linkcheck`, `traceability-guard`, `process-coherence-guard`, `stakeholder-cadence-guard`) have `allow_failure: true`. Command: `glab mr merge <n> --yes --auto-merge --sha <head>`. Do not rebase on conflicts (SSE). Do not `terraform apply` as MRC. Loop ticks must not merge.

---

## 7. Still open (probe before acting)

Actionable:

- **#270** (high, Path B Anthropic 2.0s timeout) — implement, do not mark done in a memory log first.
- **#257** (verify job / single role-list). Knowledge node is on main; job is **not** implemented. Generator ACTIVE reprint lives here.
- **CF-049** loop `queued` on `origin/main`. Audit-script TTFB relabel already landed (`dd48525`, [[2026-08-23-session-memory-log-cf049-lcp-audit-script-honest-labeling]]). Remaining surface is M15 roadmap/SSR language vs static SPA. Do not mark `verified` from a KT note without CG intake + issue + MR.
- **CF-050…053** still `queued`. A 2026-08-24 commit message claimed to “resolve CF-050”; the loop row is still `queued`. Trust the loop + GitLab, not the commit subject.

Parked / future: #254 M12 CRM (PO unpark), #231 HLD/LLD, #211, #27, #35, #36, epics #13–#19.

Unissued DSO (do not reuse #270/#266): add `litellm` to `deploy-ecs`; Grafana ECR on `EcrPush`; local Terraform vs AWS drift (Grafana task, ALB `:80`, SG).

---

## 8. Incident: uncommitted overclaim on 2026-08-27 (this session)

Before this covering node was written, the working tree on `main` had:

- Uncommitted `request_timeout` / `AEA_AI_TIMEOUT` `2.0` → `2.5` (the #270 change, on `main`, no branch).
- Uncommitted loop row CF-049 `queued` → `verified` with no GitLab issue/MR.
- Untracked session logs that described both as already remediating/verified.
- DATE_RE section 3 rewritten to cite those untracked files.

That is the same failure class as CF-048. Those files were **restored/deleted**, not committed. Do not resurrect them. Do not treat mtime of a local `research/random-thoughts/` file as evidence.

---

## 9. Operating rules to inherit

1. Knowledge First: latest **committed** DATE_RE, then vault, then `glab issue list` before `glab issue create`.
2. One finding → one issue → one branch from `origin/main` → one MR. MRC only merges.
3. `glab` not `gh`. Canonical remote: `gitlab.com/artof-group/adaptive-experience-architecture`.
4. PowerShell: no bash `&&` / HEREDOC; watch `${` in strings.
5. Docker integration before MR for impacted edge/platform. Docs/Cursor-rule/research-note: no Docker.
6. Wikilinks only to vault notes or ADR/FR/NFR ids. `.cursor/` SOPs are markdown links; a wikilink into `.cursor/skills/` is a broken graph edge.
7. Do not invent BG/US/FR/NFR or CF ids.
8. Chat is not the bus. If it is not on `main`, later agents do not have it.

---

## 10. Graph links

Vault notes:

- [[2026-08-25-trust-but-verify-job-and-single-role-list]]
- [[2026-08-26-date-re-bus-and-agent-runner-image-roll]]
- [[2026-08-24-24-hour-lessons-learned-retrospective]]
- [[2026-08-23-session-memory-log-cf049-lcp-audit-script-honest-labeling]]
- [[2026-08-23-session-memory-log-cross-chat-knowledge-extraction]]
- [[2026-08-23-claude-view-repository-progression-and-alignment]]
- [[2026-08-21-kb-project-building-lessons]]
- [[2026-08-21-session-memory-building-process-and-lessons-learned]]

ADRs: [[ADR-016]] [[NFR-003]]

SOPs (markdown links; `.cursor/` is outside the wikilink resolver):

- [session-start-briefing.mdc](../../.cursor/rules/session-start-briefing.mdc)
- [coherence-findings-sop.mdc](../../.cursor/rules/coherence-findings-sop.mdc)
- [antifragility-cornerstone-sop.mdc](../../.cursor/rules/antifragility-cornerstone-sop.mdc)
- [aea-knowledge-guardian/SKILL.md](../../.cursor/skills/aea-knowledge-guardian/SKILL.md)
- [aea-mr-coordinator/SKILL.md](../../.cursor/skills/aea-mr-coordinator/SKILL.md)
- [aea-coherence-guardian/SKILL.md](../../.cursor/skills/aea-coherence-guardian/SKILL.md)
