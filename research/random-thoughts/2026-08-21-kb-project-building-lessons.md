# KB capture — AEA project building + lessons learned

tags: #aea #second-brain #project-building #lessons-learned
status: random-thoughts
captured: 2026-08-21
updated: 2026-08-21 ~15:25 Europe/Paris
canonical: C:\projects\code\adaptive-experience\research\random-thoughts\2026-08-21-kb-project-building-lessons.md
moved_from: research/inbox/2026-08-21-kb-project-building-lessons.md (stub remains)

**Living store:** **this file** in **this git repository** at `C:\projects\code\adaptive-experience\research\random-thoughts\2026-08-21-kb-project-building-lessons.md`. Not Notion. Not `C:\data\vaults\…`. Not an external Obsidian vault. Inbox is a pointer only.

**Sibling session memory:** `research/random-thoughts/2026-08-21-session-memory-building-process-and-lessons-learned.md` — do not merge; that log is a different narrative. This file owns the Project + Learning records.

**Schema used:** Notion plugin skills `knowledge-capture` + `create-page` mapped onto `research/templates/inbox-note.md`. **Three** typed records in **one** random-thoughts file: two Project (AEA + `artof-project`) + one Learning. Promotion candidate block is **not** ready — do not write a separate candidate yet.

Do not invent BG/US/FR/NFR IDs. Do not start M12, M14, or live Stripe integration. No terraform. No commit unless a later session is asked to.

**Payments (sponsor 2026-08-21 ~15:24):** target = **Stripe**; current = **mockup**. Live Stripe SDK / budget / secrets stay UNKNOWN until sponsor shares later. Do not treat “Stripe” as unpark payments. PO does not need to unpark Stripe now.

---

## Questions for sponsor / PO

Only real gaps. Ask; do not invent. **Do not ask sponsor** to close M8/M9/M10/M11/M12 or Path B product-accept — those stay with PO.

### Sponsor (human) — answered this session (2026-08-21 ~15:20 Europe/Paris)

| # | Question | Answer (authoritative) |
|---|---|---|
| 1 | Path B / `aea-pilot` budget | **Leave UNKNOWN.** Sponsor will share a number later. Do not invent. |
| 2 | Legal / commercial org | **`artof-group` is enough.** No extra legal name on these records. |
| 3 | GitLab `artof-group/artof-project` in-scope? | **Yes — include it.** Second Project record below. |
| 4 | Private / fleeting notes | **In-repo** `c:\projects\code\adaptive-experience\research\random-thoughts\` (this git tree). Not `C:\data\vaults\cts`, not `C:\data\vaults\aea`, not an external Obsidian vault, not inbox-only. |
| 5 | If M14 ever proceeds: budget / secrets | Target payment = **Stripe**; **current = mockup**. Live Stripe secrets/budget stay **UNKNOWN** until sponsor shares later. Domain / SSO / Multi-AZ: not sponsor spend this answer. **M12 stays parked** until PO unparks. Do **not** start Stripe integration, M12, or M14. “Stripe” ≠ unpark payments. PO does not need to unpark Stripe now. |

Sponsor remaining: Path B / `aea-pilot` **budget number**, and **live Stripe secrets** later. Both UNKNOWN.

### Product Owner (`@aea-product-owner`) — still UNKNOWN (do not invent)

1. **M8 close?** — Roadmap table says M8 Completed. GitLab group milestone **M8 — Returning shopper** is still **active**. Parent **#27** is still **open**, labels `scope::future`. Should the GitLab milestone be closed, or does FR-008 remainder keep M8 open?
2. **M9 go/no-go** — `research/daily-briefs/2026-08-21.md` claims PO accepted M9 after 24h soak. `.cursor/skills/aea-product-owner/SKILL.md` has **no dated accept**. GitLab M9 is still **active**, 0 open issues. Accept, defer, or park M9 as a **product** slice? (Telemetry enough ≠ closed-loop validated; runner is still an HTTP stub.)
3. **M10 close?** — Roadmap table says Completed (palette / pet-safety slice). GitLab M10 still **active**, 0 open issues. Workbook free-form FR-003 remainder is still Future. Close the GitLab milestone, or keep it open for the remainder?
4. **M11 park?** — Prior notes said sponsor parked M11. GitLab M11 is **active**, 0 open issues. The 21 Aug brief assigns Stream 2 to M11. Confirm: **park**, **defer**, or **accept** a named FR-012 / NFR-010 slice?
5. **M12 park vs table** — PO skill: M12 **stays parked** until this skill names unpark. Roadmap **table** says Unparked. GitLab M12 **active**. **#35 / #36** open, `scope::future`. This capture **does not start M12**. Please confirm park still holds and whether the roadmap table should be corrected (own CF/MR later).
6. **Path B product accept** — Path B shop is live (`https://aea.artof.link/healthz` → `{"status":"ok"}`). DSO apply is already unparked. Has PO **product-accepted** Path B as the reference shop, or is that still open?
7. **M13 / M14 and LOAD/UX/AFG/GAP labels** — On `main` (`3b245f6`) the roadmap table adds M13 and M14 and cites `LOAD-001..004`, `AFG-001..004`, `UX-001..002`, `GAP-001..005`. Those strings are **not** archive BG/US/FR/NFR IDs. GitLab has **no** M13/M14 group milestones. Are they product-accepted named milestones, or briefing labels only (park until a promote that does not mint archive IDs)?

Sponsor (this session): **PO does not need to unpark Stripe now.** Questions 1–7 stay unanswered. Do not invent answers.

---

## Verification stamp (this pass)

Fetched **Friday 21 Aug 2026 ~15:06 Europe/Paris**; sponsor answers **~15:20**; path correction + Stripe mockup **~15:25 Europe/Paris**. `artof-project` re-fetched (`empty_repo: true`). !252 verified this pass. Do not copy the 21 Aug daily brief’s Stream 2 / M12 / “13/13 guards” numbers as authority.

| Fact | Verified value | Source |
|---|---|---|
| Repo | `c:\projects\code\adaptive-experience` | workspace |
| Branch | `main` = `origin/main` | git |
| `main` SHA | `3b245f6eee44ebbf8c7124faef6b6f1dc28f9935` | `git rev-parse origin/main` |
| `main` tip | `docs(roadmap): create Milestones M13 and M14…` 2026-08-21 14:52:29 +0200 | git log |
| Daily brief `2026-08-21.md` | **Committed** on that SHA (not local-only). Treat Stream 2 M11/M12 assignment as **conflict**, not unpark. | `git log -- research/daily-briefs/2026-08-21.md` |
| GitLab project | `artof-group/adaptive-experience-architecture` (id 85239039) | `glab repo view` / API |
| Path A | Local Docker Compose + `python platform/scripts/run_integration_tests.py` / `python edge/scripts/run_integration_tests.py` | skills / docker-integration SOP / `infra/aws/README.md` (Compose ≠ NFR-007/012 prod proof) |
| Path B live | `GET https://aea.artof.link/healthz` → 200 `{"status":"ok"}` | this pass |
| Path B cloud stub | `GET https://aea.artof.link/cloud/status` → 200 `autonomous_loop_enabled:true`, `cluster:aea-pilot`, `service:aea-agent-runner`, `secret_name:aea/gitlab-token`, `status:active` | this pass |
| Webhook GET | `GET https://aea.artof.link/webhooks/gitlab` → **405** (POST only). Do not forge payloads. | this pass |
| !259 | merged `8de13a1` 2026-08-19T22:18:27Z; MR HEAD `1d291b6`; pipeline iid **909** success with warnings | `glab` MR 259 |
| !263 | merged `9d86611` 2026-08-20T13:01:13Z | `glab` MR 263 |
| Pipeline **921** | GitLab **iid** 921 (API id `2776203108`), `sha=9d86611`, `ref=main`, `status=success`, source `push`, 2026-08-20T13:01:14Z. `GET .../pipelines/921` 404s because the API wants numeric **id**, not iid. | `glab api pipelines?per_page=20` |
| Coverage | Pipeline objects have `"coverage":null`. No `pytest-cov` in `.gitlab-ci.yml`. Tests: `python -m unittest discover`. | this pass + grep |
| LangGraph | No `langgraph` / `LangGraph` dependency in repo (only this inbox note). `research/loop-graph.md` is the CI-guarded **process** graph. Later. | grep |
| Cloud runner | HTTP stub: `trigger_autonomous_remediation` returns dict `"status":"triggered"` / `"action":"auto_remediation_draft_created"` with **no** `glab`. MRC-only merge. | `platform/aea_platform/agent_gateway.py` |
| Skills on `main` | **13 committed** canonical `.cursor/skills/aea-*/SKILL.md` including `aea-knowledge-guardian` (`e925cb9`, 2026-08-21 14:28 +0200) and `aea-cost-guardian` (`3617c2f`, 2026-08-21 14:39 +0200). Not untracked. | `git ls-files`; `git log` |
| SOP drift | `.cursor/rules/stakeholder-skills-sync-sop.mdc` still says **11 roles**. `AGENTS.md` says **13**. Generator `SKILLS` has 13 keys. | disk |
| Guards list | `scripts/run_all_guards.py` `GUARDS` has **14** tuples; file docstring still says “all 13”. Antifragility SOP says 14/14. Brief says 13/13. **Not re-run this pass.** | disk |
| Open MRs | !264 daily brief 2026-08-21; !260 daily brief 2026-08-20 | `glab mr list` |
| M13/M14 GitLab | **Absent** from group milestones API | `glab api groups/artof-group/milestones` |
| GitLab `artof-project` | id 85225945; `empty_repo:true`; `readme_url:null`; tree/README **404**; issues `[]`; MRs `[]`; last activity = created 2026-08-07T20:38:52Z | `glab api` this pass |
| Payment mockup | **!252** merged 2026-08-19 (`e02b09f` / merge commit `b0869c1`); title stripe-mock simulation; Closes **#244** (not issue #252). File `platform/aea_platform/payment.py` (`PaymentSimulationEngine`, `tok_visa` / `tok_chargeDeclined`). Tests `platform/tests/test_payment.py`. Guard in `scripts/run_all_guards.py`. Existing FR-019. No live Stripe SDK. | `git log` + `glab api .../merge_requests/252` |

### GitLab group milestones (live)

M0–M7 **closed**. Still **active**: M8, M9, M10, M11, M12, UX alignment, Future Backlog. No M13, no M14.

| Milestone | GitLab state | Open issues this pass |
|---|---|---|
| M8 — Returning shopper | active | **#27** open (`scope::future`) |
| M9 — Assistant reliability | active | none |
| M10 — Compositional T-04 | active | none |
| M11 — Inventory analytics depth | active | none |
| M12 — Engagement CRM | active | **#35**, **#36** open (`scope::future`) |

#35 title FR-016; #36 title FR-017; both milestone “M12 — Engagement CRM”.

---

# Record 1 — Project building (type: Project)

## Inbox-note template fields

| Field | Value |
|---|---|
| **title** | Adaptive Experience Architecture (AEA) — Lily's Florist reference — project building |
| **tags** | `#aea` `#inbox` `#project-building` `#lilies-florist` `#path-a` `#path-b` |
| **status** | random-thoughts (in-repo) |
| **captured** | 2026-08-21 |
| **Note** | See Overview / Goals / Timeline / Tasks / Risks below |
| **Links** | See ## Links |
| **Open questions** | See ## Questions for sponsor / PO |

## Documentation Database properties (`knowledge-capture`)

| Field | Value |
|---|---|
| **Title** | Adaptive Experience Architecture (AEA) — Lily's Florist reference — project building |
| **Type** | Project |
| **Category** | Architecture / executable reference-foundation |
| **Tags** | `#aea` `#project-building` `#lilies-florist` `#path-a` `#path-b` |
| **Last Updated** | 2026-08-21 (~15:20 Europe/Paris) |
| **Owner** | `@aea-product-owner` (product go/no-go); `@aea-project-manager` (Scrum/process); human = **project sponsor** only |

## Project page sections (`create-page`)

### Overview

AEA is an architecture and executable reference-foundation repository. Lily's Florist is the **reference design**, not a second product. Legacy archive label **Quantic** appears in `archive/` filenames only.

- Canonical requirements and design: `docs/`, `implementations/`. Requirements counts SoT: `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx` (7 BG · 7 EP · 23 US · 17 NFR-US · 23 FR · 17 NFR · 40 mapping rows). Do not mint IDs.
- Product-neutral runtime: `platform/` (PostgreSQL, outbox, Kafka, orchestration) and `edge/` (TLS gateway, BFF, browser UI).
- **Path A:** local Docker Compose + platform/edge integration runners. Compose is **not** NFR-007 / NFR-012 or ADR-012 production proof (`infra/aws/README.md`).
- **Path B:** applied AWS stack `infra/aws` (ECS Fargate, ALB+ACM, RDS PostgreSQL 16, MSK TLS+SASL). Live shop: `https://aea.artof.link/`. Path B apply is unparked for `@aea-devsecops-platform`; PO owns Path A vs Path B **product** acceptance, not `terraform apply`. Sponsor owns secrets / `.env` / `terraform.tfvars` / GitLab CI var paste / `terraform destroy`.
- GitLab: `artof-group/adaptive-experience-architecture`. Tracker is GitLab (`glab`), not GitHub.
- **Budget:** UNKNOWN — sponsor will share a Path B / `aea-pilot` number later. Do not invent.
- **Org:** **`artof-group` is enough** (sponsor, this session). No extra legal/commercial name on this record.
- **Fleeting notes:** in-repo `c:\projects\code\adaptive-experience\research\random-thoughts\` (this git tree). This file is the Project + Learning capture. Not `C:\data\vaults\cts`, not an external vault, not inbox-only.
- **Payments:** target = **Stripe**; current = **mockup**. Live Stripe secrets/budget UNKNOWN until later. Do not start Stripe integration. PO does not need to unpark Stripe now.

North star (`README.md`): AI-native applications where shared understanding continuously reshapes the workspace without disrupting flow. Vision (`docs/01-product-vision/product-vision.md`): customers express needs naturally; the interface evolves as understanding grows. Cite existing BG-001…BG-007; do not rewrite vision without an explicit promote.

### Sibling / related projects

| Name | Evidence | In-scope for this KB? |
|---|---|---|
| **AEA / Lily's Florist reference** | This repo + GitLab project 85239039 | **Yes** — the Project record |
| **Lily's Florist** as a separate commercial shop | Reference design only; M14 roadmap row names `shop.lilysflorist.com` which is **not** a GitLab project | Not a sibling repo. Payments: **target Stripe / current mockup** (!252). Live Stripe secrets UNKNOWN. Domain / SSO / Multi-AZ: not sponsor spend. Whether M14 is a product milestone: still **PO q7**. |
| **`artof-group/artof-project`** | GitLab id 85225945, private, `empty_repo: true`, no README commit, last activity 2026-08-07 (create) | **Yes — in-scope** (sponsor). See Record 2. Goals UNKNOWN. |
| **Quantic** | Archive workbook filename only | Historical packaging, not a current project |

No other GitLab projects under `artof-group` were returned by `groups/artof-group/projects?per_page=100`.

### Goals

1. Deliver the Lily's Florist Adaptive Workspace (tiles T-01…T-09, ASO FAQ, thin Contact Florist) against existing FR/NFR IDs.
2. Keep Path A Compose and Path B `aea.artof.link` honest: fail-closed inventory, no seeder on production Path B, named `aea-pilot` florist exception only.
3. Run the committed stakeholder team with six-way skill portability (Cursor / Codex / Claude / Copilot / Gemini / Grok). **Verified 13 committed roles** on `main`; SOP file still says 11 — process drift, not a reason to invent a 14th.
4. Merge only via `@aea-mr-coordinator`. Loop ticks must not merge.
5. Do **not** start M12 CRM (FR-016 / FR-017, GitLab #35 / #36, `scope::future`) until PO names unpark. Sponsor restated this session: M12 stays parked until PO unparks. Do not treat that as PO closing q5 (roadmap table vs GitLab vs skill still conflict).

### Timeline

Evidence as of **Friday 21 Aug 2026 ~15:06 Europe/Paris** (GitLab + `main` + live Path B this pass).

| Milestone | Roadmap table (`docs/07-roadmap/roadmap.md` @ `3b245f6`) | GitLab group milestone | Operational authority (PO skill + this capture) |
|---|---|---|---|
| M0–M7 | MVP pipeline (published) | **closed** | MVP delivered / hardening lane |
| **M8** Returning shopper (FR-008) | **Completed** | **active**; #27 open Future | **Label-conflict.** Ask PO whether to close GitLab M8. Roadmap notes still say “Do not start M12 while M8 is open.” |
| **M9** Assistant reliability (NFR-008) | **Completed** | **active**; 0 open issues | Brief claims PO accept; **no dated PO artifact in the skill**. Soak telemetry **enough** 20 Aug; cloud runner remains HTTP stub. Ask PO go/no-go. |
| **M10** Compositional T-04 (FR-003 remainder) | **Completed** (palette / pet-safety slice) | **active**; 0 open issues | **Label-conflict** — workbook free-form remainder stays Future. Ask PO whether to close GitLab M10. |
| **M11** Inventory analytics (FR-012, NFR-010) | Open row (not Completed) | **active**; 0 open issues | Prior capture: parked. Brief assigns Stream 2. Ask PO park/defer/accept. Do not treat the brief as unpark. |
| **M12** Engagement CRM (FR-016, FR-017) | Table **Unparked** | **active**; #35 #36 Future | **Do not start.** PO skill: stays **parked** until PO names unpark. Ask PO to reconcile the table. |
| **M13** Load & Anti-Fragile Hardening | Present on `main` (LOAD/AFG labels) | **not in GitLab** | Not archive IDs. Ask PO whether this is a real milestone. Do not start as if accepted. |
| **M14** Production Go-Live & FinOps | Present on `main` (GAP/UX labels) | **not in GitLab** | **Do not start.** Target payment = Stripe; current = mockup (!252). Live Stripe secrets UNKNOWN. Domain / SSO / Multi-AZ not sponsor secrets. Still **PO q7**. PO does not need to unpark Stripe now. |
| Future Backlog | Unscheduled remainder | **active** | Voice, semantic cache, other industries |

24h Path B soak: started **2026-08-19 14:00 Europe/Paris**; evaluated **2026-08-20 ~14:25 Paris**; elapsed ~24h 21m. Verdict: ALB+CloudWatch trail **enough**, not a single 200. Re-probed this pass: healthz ok, `/cloud/status` stub, webhook GET 405.

### Tasks

Active / next (existing IDs and process only — no new FR/NFR):

- Keep M12 parked (#35 / #36). Do not assign CRM schema work as “in progress.” Sponsor: stays parked until PO unparks.
- Do not start M13/M14 from the roadmap table until PO answers question 7. Payments stay **mockup** (`platform/aea_platform/payment.py`, !252). Do not start live Stripe. Live secrets UNKNOWN.
- Keep M11 out of Stream 2 until PO answers question 4.
- Reconcile M8/M10/M12 **label-conflicts** (roadmap table vs GitLab vs PO skill vs workbook Future) as separate coherence findings if still open — one finding → one issue → one branch → one MR. **Not this capture.**
- Cloud runner follow-up (separate MR after nginx fix): POST `/webhooks/gitlab` should use secret `aea/gitlab-token` for acknowledge vs draft-only; **no unattended merge**.
- Advisory CI (`allow_failure: true` on `traceability-guard`, `process-coherence-guard`, `stakeholder-cadence-guard`, etc. in `.gitlab-ci.yml`) is **not** merge authority.
- SOP vs `AGENTS.md` role-count (11 vs 13) is process docs drift — own later MR; do not invent roles here.

### Risks

- Roadmap M12 “Unparked” vs PO “stays parked” vs 21 Aug brief “Stream 2 M11 & M12” — agents will start M12 if they trust the table or the brief.
- M13/M14 landed on `main` in `docs/07-roadmap/roadmap.md` **without** GitLab milestones and with non-archive labels (`LOAD-*`, `AFG-*`, `UX-*`, `GAP-*`). Risk: agents treat those as FR/NFR-class work.
- ECS `aea-agent-runner` advertises `autonomous_loop: true` while `process_gitlab_webhook` / `trigger_autonomous_remediation` return dicts only (`platform/aea_platform/agent_gateway.py`). `/cloud/status` is an env-flag echo (verified live this pass).
- CI tags `:latest` and `$CI_COMMIT_SHA` (`.gitlab-ci.yml` `build-ecr`). First Path B deploys can pull **stale `:latest`** while an older ECS task still serves.
- Dirty `main` leftovers previously crashed nginx (`unknown directive "<<<<<<<"`). !263 cleaned syntax; Grafana `/grafana/` later went through !265 (brief). Do not mix leftovers into unrelated MRs.
- Stakeholder-skills-sync SOP still says 11 roles while `main` has 13 committed skills — generator `--check` can pass adapters while always-apply SOP text is stale.

---

# Record 2 — Sibling GitLab project `artof-project` (type: Project)

## Inbox-note template fields

| Field | Value |
|---|---|
| **title** | artof-group/artof-project — in-scope sibling (empty repo) |
| **tags** | `#aea` `#inbox` `#project-building` `#artof-project` |
| **status** | random-thoughts (in-repo) |
| **captured** | 2026-08-21 |
| **Note** | Empty GitLab project; sponsor included it in this KB. Goals UNKNOWN. |
| **Links** | https://gitlab.com/artof-group/artof-project |
| **Open questions** | Goals UNKNOWN (no README, no description). Remaining PO questions live on Record 1 — do not invent FRs for this repo. |

## Documentation Database properties (`knowledge-capture`)

| Field | Value |
|---|---|
| **Title** | artof-group/artof-project |
| **Type** | Project |
| **Category** | Sibling GitLab repository (empty) |
| **Tags** | `#aea` `#artof-project` `#artof-group` |
| **Last Updated** | 2026-08-21 (~15:20 Europe/Paris) |
| **Owner** | Project sponsor (include/exclude). No product owner or FR inventory named for this empty repo. |

## Project page sections (`create-page`)

### Overview

GitLab **`artof-group/artof-project`** (id **85225945**), private, created **2026-08-07T20:38:52Z**. Sponsor (this session): **in-scope** for this AEA knowledge store. Org name on the record: **`artof-group` is enough**.

Verified this pass (`glab api projects/artof-group%2Fartof-project` and related endpoints):

- `empty_repo`: **true** (not “a README that happens to be blank”)
- `readme_url`: **null**
- Default branch name is `main`, but `repository/files/README.md?ref=main` and `repository/tree` return **404 Commit/Tree Not Found** — there is **no commit**
- Issues: **[]**; merge requests: **[]**; `open_issues_count`: **0**
- `description`: null
- Last activity: **2026-08-07T20:38:52Z** (same instant as create — no later push)

Do not invent FR/NFR IDs, milestones, or product goals for this project. It has no archive mapping.

### Goals

**UNKNOWN.** No README, no description, no issues, no tree. Capture the emptiness; do not fill goals from AEA’s Lily's Florist FR set.

### Timeline

| Date | Evidence |
|---|---|
| 2026-08-07T20:38:52Z | GitLab project created; last_activity same timestamp |
| 2026-08-21 | Sponsor: include in this KB store |

### Tasks

None in this repo. Do not start work here from this capture. Do not terraform. Do not mint IDs.

### Risks

- Agents may treat this as a second product and copy AEA FR IDs. There is no archive workbook for `artof-project`.
- Empty `main` means a clone has nothing to check out until someone pushes.

---

# Record 3 — Lessons learned (type: Learning)

## Inbox-note template fields

| Field | Value |
|---|---|
| **title** | AEA lessons learned — building process, merge/ops, soak vs “validated” (2026-08-19…21) |
| **tags** | `#aea` `#inbox` `#lessons-learned` `#merge` `#path-b` `#graph-loop` `#mrc` |
| **status** | random-thoughts (in-repo) |
| **captured** | 2026-08-21 |
| **Note** | See Learning sections below |
| **Links** | See ## Links |
| **Open questions** | See ## Questions for sponsor / PO |

## Documentation Database properties (`knowledge-capture`)

| Field | Value |
|---|---|
| **Title** | AEA lessons learned — building process, merge/ops, soak vs “validated” (2026-08-19…21) |
| **Type** | Learning |
| **Category** | Process / operations post-mortem |
| **Tags** | `#aea` `#lessons-learned` `#merge` `#path-b` `#graph-loop` `#mrc` |
| **Last Updated** | 2026-08-21 (~15:20 Europe/Paris) |
| **Owner** | `@aea-project-manager` (process); `@aea-mr-coordinator` (merge); `@aea-coherence-guardian` (queue/briefs); `@aea-knowledge-guardian` (this living store, now committed) |

## Learning sections (`knowledge-capture`)

### What Happened

1. **Role split (sponsor vs SM vs PO).** Human is **project sponsor**, not Scrum Master. `@aea-project-manager` **is** SM. `@aea-product-owner` owns mission/vision/backlog-among-existing-IDs and product go/no-go (accept / defer / park), including M12 unpark recommendation. Evidence: `.cursor/skills/aea-project-manager/SKILL.md`, `.cursor/skills/aea-product-owner/SKILL.md`, `research/inbox/sponsor-sm-skill-gaps.md`.
2. **Committed stakeholder roles on `main`:** **13**, not 11 and not “untracked 12th.” Roster: `aea-project-manager`, `aea-product-owner`, `aea-ux-designer`, `aea-customer-journey`, `aea-support-coordinator`, `aea-ai-engineer`, `aea-appsec-auditor`, `aea-devsecops-platform`, `aea-senior-software-engineer`, `aea-mr-coordinator`, `aea-coherence-guardian`, **`aea-knowledge-guardian`**, **`aea-cost-guardian`**. Six-way adapters exist (Cursor canonical → Codex `.agents/` → Claude `.claude/` → Copilot `.github/instructions/` → Gemini `.gemini/` → Grok `.grok/`). SOP file text still says 11 — **docs drift**.
3. **Merge authority.** Only `@aea-mr-coordinator` may set auto-merge (`glab mr merge <n> --yes --auto-merge`). Remediation loop ticks, hourly `/loop`, and sibling skills **must not merge** unless MRC was invoked.
4. **Graph loop ≠ LangGraph.** `research/loop-graph.md` is a **CI-guarded process graph** (`loop-graph-guard` → `scripts/check_loop_graph.py`). Repo grep finds **no** `LangGraph` / `langgraph` dependency. LangGraph (or any runtime graph library) is **later**, not this milestone.
5. **Cloud runner is an HTTP stub (still true live).** FastAPI `GET /cloud/status` → 200 env echo; `GET /webhooks/gitlab` → 405. `trigger_autonomous_remediation` returns `"status": "triggered"` without calling `glab`. Secret **name** `aea/gitlab-token` advertised; value not read this pass. **No unattended merge.**
6. **Recent Path B ops (re-verified):**
   - !259 nginx webhooks/cloud routes merged **`8de13a1`** (2026-08-19T22:18:27Z; MR HEAD `1d291b6`). Pipeline **909** success with warnings.
   - Conflict-marker nginx crash after leftovers. Fix !263 merged **`9d86611`**. Post-merge pipeline **iid 921** (id `2776203108`) **success** on `main` @ `9d86611`. Path B healthz 200 this pass.
7. **24h soak.** Started 19 Aug 14:00 Paris; telemetry **enough** 20 Aug (~14:25 Paris). Do not call Path B “validated closed-loop.”
8. **21 Aug `main` moved** to `3b245f6` (M13/M14 roadmap rows) **after** the earlier inbox dump. GitLab milestones were **not** created for M13/M14. Daily brief on that commit assigns Stream 2 M11 & M12 — **conflict** with PO park.

### What Went Well

- One-finding SOP is written and CI-adjacent: one finding → one GitLab issue → one branch from updated `origin/main` → one MR.
- Six-way skill sync is mechanically checked (`generate_codex_stakeholder_skills.py --check`); knowledge-guardian and cost-guardian are now in the generator inventory (committed).
- Edge Docker integration is a **blocking** CI job (`edge-docker-integration`); advisory jobs are labeled `allow_failure: true`.
- Soak used a 24h ALB + CloudWatch trail, not a single probe — correct bar for Path B.
- Sponsor vs SM overlap was fixed by giving SM to PM and creating PO; secrets paste stays human.
- Living KB decision: in-repo `research/random-thoughts/` (this git tree), not Notion, not `C:\data\vaults\…`.

### What Didn't

- **Dirty `main` leftovers piggybacked** (Grafana public `/grafana/` mixed with cart/`e50b447`). Unresolved conflict markers crashed nginx. Grafana belongs in its own MR (later !265), not the nginx-syntax fix.
- **Advisory CI ≠ merge authority.** Pipeline 909 “success with warnings” does not mean MRC gates passed or that a loop tick may merge.
- **Calling cloud “validated” too early.** `/cloud/status` 200 + webhook stub 200 ≠ autonomous loop. Still true on live Path B this pass.
- **Stale `:latest`.** Dual-tag ECR push without pinning the running task to `$CI_COMMIT_SHA` lets the first roll pull yesterday’s image.
- **Briefs vs skills vs roadmap vs GitLab.** 21 Aug brief assigns Stream 2 **M11 and M12**; roadmap table marks M12 Unparked and M8/M9/M10 Completed; GitLab keeps M8–M12 **active**; PO skill keeps M12 parked. Agents that trust a brief will start M12.
- **pytest-cov:** no measured coverage %. Tests are `python -m unittest discover`. Guards + Docker/CI, not a coverage gate. Pipeline `coverage` field is null.
- **SOP not updated with roles.** Knowledge-guardian was treated as “untracked 12th” in the previous dump; it is now committed, plus cost-guardian, while the always-apply SOP still lists 11.

### Root Causes

- Batching unrelated leftovers onto `main` (Grafana + cart + conflict markers) violated one-finding-one-MR.
- Stub HTTP endpoints named like a closed loop (`autonomous_loop: true`, `trigger_autonomous_remediation` returns `"status": "triggered"` without `glab`).
- `:latest` as a deploy alias plus ECS not waiting for new task health before calling Path B “on the new nginx.”
- Daily briefs synthesized “Stream 2 M11 & M12” without a PO unpark artifact; roadmap table drifted from PO hard constraint and from GitLab milestone **state**.
- Coverage % was never a stated NFR gate; unittest + Compose/CI was the actual contract.
- Role roster changed on `main` (13 skills) faster than the always-apply SOP text (11).

### Actions

1. **Do not start M12.** PO must name unpark; #35 / #36 stay Future. Sponsor this session: stays parked until PO unparks (not a PO q5 close).
2. **Do not start M13/M14** or live Stripe. Target = Stripe; current = mockup (!252). Live secrets UNKNOWN. PO does not need to unpark Stripe now.
3. **Do not treat M11 as unparked** because a brief said Stream 2.
4. **MRC-only merge.** Loop ticks do not merge. Dirty leftovers → own issue/MR.
5. Treat `allow_failure` jobs as advisory review for PM-SM, not a green merge signal.
6. Require soak/telemetry **and** a non-stub runner before saying cloud loop is validated. Next runner slice: use `aea/gitlab-token` for acknowledge/draft-only; still **no unattended merge**.
7. Prefer image digest / `$CI_COMMIT_SHA` on ECS task defs over floating `:latest`.
8. LangGraph: **later**. Keep `research/loop-graph.md` as the process graph.
9. Promote from this **random-thoughts** note only with a tight docs/process MR if labels still conflict — one conflict per MR. SOP 11→13 is a separate process MR, not this capture.

## Decision log fields (`knowledge-capture`)

| Field | Value |
|---|---|
| **Decision** | Living knowledge stays in git (`research/` → `docs/` via Obsidian loop). Notion may mirror a snapshot later; it is not SoT. |
| **Date** | 2026-08-21 |
| **Status** | Accepted (sponsor clarification this session) |
| **Domain** | Knowledge management / process |
| **Deciders** | Project sponsor (human); PM-SM for process; PO for product go/no-go |
| **Impact** | Agents evolve **in-repo** `research/random-thoughts/` (this git tree) and canonical `docs/`; inbox is a stub pointer; no `C:\data\vaults\…`; no parallel Notion authority |

| Field | Value |
|---|---|
| **Decision** | GitLab `artof-group/artof-project` is in-scope. Org = `artof-group` (enough). Path B / `aea-pilot` budget UNKNOWN. Payments: **target Stripe / current mockup** (!252). Live Stripe secrets UNKNOWN. M12 stays parked until PO unparks. Living KB path is in-repo `research/random-thoughts/`. |
| **Date** | 2026-08-21 |
| **Status** | Accepted (sponsor answers this session) |
| **Domain** | Knowledge scope / spend boundary |
| **Deciders** | Project sponsor (human) |
| **Impact** | Second Project record for the empty sibling repo; do not invent its goals or FR IDs; do not start M12 or M14 from this capture |

| Field | Value |
|---|---|
| **Decision** | PM is Scrum Master; human is sponsor; PO owns product go/no-go including M12 park |
| **Date** | 2026-08-18 (skill/inbox) — still in force 2026-08-21 |
| **Status** | Accepted |
| **Domain** | Governance |
| **Deciders** | Sponsor + PM skill + PO skill |
| **Impact** | Cadence/bench without waiting on sponsor; secrets still `user` wait tag |

| Field | Value |
|---|---|
| **Decision** | Path B `https://aea.artof.link/` unparked for DSO apply; Path A remains Compose |
| **Date** | In force (DSO `SKILL.md` / `infra/aws/README.md`); live healthz 200 this pass |
| **Status** | Accepted (DSO apply). **Product accept of Path B as the shop:** UNKNOWN — ask PO (question 6) |
| **Domain** | Deployment |
| **Deciders** | PO (product accept Path A vs B); DSO (apply); sponsor (secrets/destroy) |
| **Impact** | Do not ask sponsor to apply terraform; do not treat Compose as production proof |

## Problem-solving extraction (`knowledge-capture`)

| Field | Value |
|---|---|
| **Problem statement** | After !259, Path B nginx needed webhook/cloud routes; a later `main` commit left conflict markers and Grafana leftovers; soak could be misread as “loop validated.” |
| **Approaches tried** | Single 200 probes; mixing Grafana into the nginx-fix MR (rejected); treating pipeline warnings as merge-OK. |
| **Solution found** | 24h ALB+CloudWatch soak (enough 20 Aug); !263 nginx syntax-only MR; Grafana in a later dedicated change (!265); stub honesty on `/cloud/status` and POST `/webhooks/gitlab`. |
| **Why it worked** | Scope stayed one finding; blocking Edge Docker CI stayed required; advisory jobs stayed advisory. |
| **Future considerations** | Wire webhook to `aea/gitlab-token` without unattended merge; pin ECS to SHA; reconcile M8/M10/M12 labels; do not start M12 or live Stripe; LangGraph later; payments stay mockup (!252); target Stripe. |

---

# Team / merge (quoted)

- **Sponsor (human):** budget, secrets, GitLab CI var paste, `terraform destroy`, explicit PO override. Not SM, not PO.
- **PM = Scrum Master:** cadence, WIP, one-finding-one-MR, bench. Does not merge, terraform, or override PO go/no-go.
- **PO:** mission/vision, priority among **existing** IDs, accept/defer/park, Path A vs Path B product acceptance, M12 unpark recommendation, what “done” means for a journey walk.
- **MRC only merge.** Loop ticks must not merge.
- Coverage: **no pytest-cov measured %**; `unittest` + Docker/CI guards.

---

## Links

- Related docs: `README.md`, `docs/01-product-vision/product-vision.md`, `docs/07-roadmap/roadmap.md`, `infra/aws/README.md`, `research/loop-graph.md`, `research/claude-obsidian-loop.md`, `research/templates/inbox-note.md`, `research/templates/promotion-candidate.md`, `.cursor/rules/stakeholder-skills-sync-sop.mdc`, `.cursor/rules/coherence-findings-sop.mdc`, `.cursor/skills/aea-project-manager/SKILL.md`, `.cursor/skills/aea-product-owner/SKILL.md`, `.cursor/skills/aea-mr-coordinator/SKILL.md`, `.cursor/skills/aea-devsecops-platform/SKILL.md`, `.cursor/skills/aea-knowledge-guardian/SKILL.md`, `.cursor/skills/aea-cost-guardian/SKILL.md`, `platform/aea_platform/agent_gateway.py`, `scripts/run_all_guards.py`, `.gitlab-ci.yml`
- Related notes: `research/inbox/2026-08-20-mr259-graph-loop-24h-soak.md`, `research/inbox/sponsor-sm-skill-gaps.md`, `research/daily-briefs/2026-08-21.md` (committed on `3b245f6`; treat Stream 2 M12 assignment as **conflict**, not unpark), `research/future-milestone-plan.md`, `research/random-thoughts/2026-08-21-session-memory-building-process-and-lessons-learned.md` (fleeting session memory — do not duplicate here)
- Fleeting notes path: in-repo `c:\projects\code\adaptive-experience\research\random-thoughts\` (this git tree). Sibling Project: https://gitlab.com/artof-group/artof-project (`empty_repo`)
- MRs: https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/252 (payment mockup) · !259 · !263 · !265 (Grafana, from brief; not re-diffed this pass)
- Live: https://aea.artof.link/healthz · https://aea.artof.link/cloud/status
- Group milestones: https://gitlab.com/groups/artof-group/-/milestones
- Issues: #27 (M8), #35 (FR-016), #36 (FR-017)
- Canvas: `canvases/kb-projects-2026-08-21.canvas.tsx` (does not replace `kb-notion-vs-obsidian-2026-08-21.canvas.tsx`)
- Notion: not written. Git is SoT. Optional future snapshot only.

## Open questions

**Sponsor remaining:** Path B / `aea-pilot` budget — UNKNOWN. Live Stripe secrets — UNKNOWN. Current payment path is mockup (!252).

**PO remaining** (same as **Questions for sponsor / PO** → Product Owner, unanswered; do not invent; do not ask sponsor to close them):

1. M8 close vs GitLab active / #27 Future
2. M9 go/no-go (brief vs no dated PO artifact vs HTTP stub)
3. M10 close vs FR-003 remainder Future
4. M11 park / defer / accept
5. M12 park vs roadmap table Unparked (sponsor restated park-until-PO; table still conflicts)
6. Path B product accept of live shop
7. M13 / M14 real milestones vs briefing labels

No additional invented gaps.

## Promotion candidate (`research/templates/promotion-candidate.md`)

**Ready for promote? No.** Stay in in-repo `research/random-thoughts/`. Budget still UNKNOWN; M8–M14 still conflict across GitLab / roadmap / PO skill / brief.

### Summary

Capture project-building facts and process lessons in git. Optionally later promote **label-conflict** rows into `docs/07-roadmap/roadmap.md` and GitLab — each as its own CF/issue/MR. Do not promote M12 unpark. Do not edit canonical docs from this inbox note until asked.

### Evidence

- Vault / inbox notes: this file; `research/inbox/2026-08-20-mr259-graph-loop-24h-soak.md`
- Fleeting notes: `research/random-thoughts/` (incl. `2026-08-21-session-memory-building-process-and-lessons-learned.md`)
- Existing git paths: listed under Links
- Live GitLab / Path B: verification stamp above

### Proposed canonical targets

| Path | Change type | Notes |
|---|---|---|
| `docs/07-roadmap/roadmap.md` | clarify (later, own MR) | M12 table “Unparked” vs notes/PO park; M8/M10 Completed vs GitLab active; M13/M14 present vs no GitLab milestones |
| `.cursor/rules/stakeholder-skills-sync-sop.mdc` | clarify (later, own MR) | 11 vs 13 committed roles — process, not product |
| `research/loop-graph.md` | none now | Already CI-guarded; not LangGraph |
| Notion wiki | none | Mirror snapshot only if sponsor asks; not SoT |

### ID impact

- [x] None (prose / structure only) for **this random-thoughts file**
- [x] Cites existing BG/US/FR/NFR IDs only (FR-008, FR-003, FR-012, FR-016, FR-017, NFR-008, NFR-010, NFR-007, NFR-012; BG-001…007 from vision)
- [ ] Would require archive/xlsx change — **no**
- LOAD/UX/AFG/GAP strings appear on `main` roadmap; they are **not** archive IDs. This note cites them as labels only.

### Risks / open questions

- Promoting roadmap label fixes without PO answers could create a new CF-039-class drift.
- Closing GitLab M8 while #27 is open Future would hide FR-008 remainder.

### Ready for promote?

- [x] Does not invent requirement IDs
- [ ] Owner path identified — process: `@aea-project-manager`; product labels: `@aea-product-owner`; this note stays in in-repo `research/random-thoughts/` until a named promote ask **and** remaining UNKNOWN (budget + PO list) are answered
- [x] Coherence SOP needed? **yes** if roadmap/GitLab labels are changed (one conflict per MR)
