# DATE_RE bus, cadence sidecar, and the 24/7 agent-runner image

> **Tags**: #aea #second-brain #honesty #knowledge-first #coherence #antifragility
> **Captured**: 2026-08-26
> **GitLab**: #267
> **Related**: #259 / !280 (CF-048), #263 / !285 (sidecar), #264 / !286 (CI jobs), #266 / !287 (OIDC ECR, unmerged), #265 (LiteLLM, DSO)
> **Owners to inherit**: @aea-knowledge-guardian, @aea-coherence-guardian, @aea-devsecops-platform, @aea-mr-coordinator
> **This node is knowledge, not a merge of product work.**

Later agents: do not rediscover this. Shared memory is committed GitLab `main` only. A status word is a claim. Probe in the same session or write Unknown.

Inherits [[2026-08-25-trust-but-verify-job-and-single-role-list]].

---

## 1. What was true on 2026-08-26

Honesty-docs loop on `main` (do not reopen as new brief tickets):

- CF-048 generator + DATE_RE filename: #259 / !280, loop `verified`
- Handoff `research/daily-briefs/2026-08-26.md` aligned: #261 / !283
- Always-loaded role count 14: #262 / !284
- Cadence must not write DATE_RE: #263 / !285

Still open, different tickets: #257 verify job, #260 Antigravity Always On (no `.agents/rules/`), #265 LiteLLM not up on Path B.

---

## 2. DATE_RE has one owner

Canonical session-start bus is `research/daily-briefs/YYYY-MM-DD.md`. Freshness CI `DATE_RE` is `^(\d{4}-\d{2}-\d{2})\.md$`.

Owner: `scripts/generate_daily_brief.py` plus an honest hand-review. Do not rerun the generator as a ritual. On this date it still hardcodes all 14 hats `` `ACTIVE` ``. That reprint is a follow-up, not a license to edit DATE_RE from a scheduled recap.

Cadence / `aea-daily-activity-report` writes `research/random-thoughts/YYYY-MM-DD-daily-activity.md` only. Skill on `main` after !285 forbids create/edit/append/restore/commit of DATE_RE. If git, glab, or bash is down: write nothing. Reflog fallback onto DATE_RE is a lie (it happened twice on 2026-08-26 as uncommitted Section 7).

The Cursor schedule prompt is **outside git**. An old cached task can ignore the skill. Pasting the DATE_RE-forbid prompt into that schedule is the stop-the-bleeding change. Do not fan the same prompt into Codex, Copilot, Gemini, Grok, or 3DX Lab. Adapters are thin pointers. 3DX Lab is a different repo.

---

## 3. 24/7 agent-runner does not git pull

`platform/docker/Dockerfile.agent-runner` does `COPY . .` at image build. `agent_gateway.py` is an HTTP stub plus baked `run_all_guards.py`. It does not run `@aea-coherence-guardian` and does not write DATE_RE.

`build-ecr` / `deploy-ecs` historically built orchestration, BFF, gateway only. Merging skills to `main` did not roll ECS `agent-runner`. `AEA_AUTONOMOUS_LOOP_ENABLED` pauses; it does not pull git. Laptop `docker push` to pilot ECR is not the path (`infra/aws/README.md`).

#264 / !286 added separate OIDC jobs `build-ecr-agent-runner` and `deploy-ecs-agent-runner` so a skill-only change does not rebuild shop images. Sponsor pastes GitLab CI var `AEA_ECR_AGENT_RUNNER` (same board as `AEA_ECR_GATEWAY`). First pipeline on `f2f59cf` built the image then push denied: role `aea-pilot-gitlab-ci` lacked `ecr:InitiateLayerUpload` on `aea-pilot/agent-runner`. DSO #266 / !287 (IAM in git; targeted apply already ran; MR unmerged at capture). Later jobs on pipeline 1049: agent-runner build+deploy succeeded; shop `deploy-ecs` failed `services-stable` wait on gateway/BFF. `litellm` is still not in that deploy list (#265).

First merge of `.gitlab-ci.yml` also fires shop `build-ecr` because both jobs list that file under `changes`. Later skill-only merges should roll `agent-runner` only.

---

## 4. Writers to watch

| Writer | Writes DATE_RE? | Note |
|---|---|---|
| `scripts/generate_daily_brief.py` | yes (owner) | Still emits all-ACTIVE hats |
| `@aea-coherence-guardian` cadence | no after !285 | Sidecar in random-thoughts |
| Cursor schedule `aea-daily-activity-report` | must not | Prompt outside git |
| Antigravity | skip Knowledge First until #260 | No `.agents/rules/` |
| ECS `agent-runner` | no | Stub; image bake only |
| This Grok Bot | no | Skills do not auto-load; `main` is the bus |

Same fail in every model: status word without a probe, DATE_RE from wedged git, PowerShell `Set-Content` on markdown, `gh` instead of `glab`, merge without MRC.

---

## 5. Related

- [[2026-08-25-trust-but-verify-job-and-single-role-list]]
- [[2026-08-23-claude-view-repository-progression-and-alignment]]
- [[2026-08-21-kb-project-building-lessons]]
- [[ADR-016]]

SOPs (markdown links; `.cursor/` is outside the wikilink resolver):

- [session-start-briefing.mdc](../../.cursor/rules/session-start-briefing.mdc)
- [aea-knowledge-guardian/SKILL.md](../../.cursor/skills/aea-knowledge-guardian/SKILL.md)
- [aea-coherence-guardian/SKILL.md](../../.cursor/skills/aea-coherence-guardian/SKILL.md)
- [aea-devsecops-platform/SKILL.md](../../.cursor/skills/aea-devsecops-platform/SKILL.md)