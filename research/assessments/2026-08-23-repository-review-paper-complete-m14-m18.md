# Coherence assessment — 2026-08-23 (repository review, paper-complete M14–M18)

tags: #aea #coherence-assessment #paper-complete
status: intake
assessed_ref: origin/main `d12c5a7` (runtime/docs claims verified there); later origin/main `02306e6` noted where docs wording moved
assessed_by: aea-knowledge-guardian (session-end persist; not a CF-queue mutation)

## Scope

- Paths reviewed: `docs/07-roadmap/roadmap.md`, `docs/03-functional-design/functional-design.md`,
  `research/daily-briefs/2026-08-22-daily-brief.md`, `research/daily-briefs/2026-08-23-daily-brief.md`,
  `research/random-thoughts/2026-08-23-repository-coherence-assessment-report.md`,
  `research/random-thoughts/2026-08-23-session-memory-log-m15-m18-execution-and-mr269-merge.md`,
  `research/coherence-findings-loop.md` (CF-001…047), `scripts/generate_daily_brief.py`,
  `scripts/apply_migrations.py` / `platform/migrations/` vs `platform/aea_platform/migrations/`,
  payment/chat/SSR/bakery/RDS evidence paths listed per claim, GitLab open MRs/issues
  (live this session)
- Checks executed: read of committed notes + generator; CF-001…047 search for equivalent claims
  (none); no new `python scripts/check_coherence.py` beyond the already-verified 14/14 pass on
  `d12c5a7`
- Exclusions / limitations: **no CF-NNN assigned to the queue this pass**; no remediation;
  no product implementation; group milestone API timed out; Cursor canvas is not a git source

Companion memory node:
[research/random-thoughts/2026-08-23-session-memory-log-repository-review-paper-complete-m14-m18.md](../random-thoughts/2026-08-23-session-memory-log-repository-review-paper-complete-m14-m18.md)

## Findings

Local `REV-*` IDs are assessment-only. Dedicated `@aea-coherence-guardian` intake should
assign the next unused stable ID (**CF-048** onward) or reuse CF-001…047 if an equivalent
claim is found. Do not treat `REV-*` as queue keys.

| Finding ID | Claim | Severity | Evidence paths | Existing issue / MR |
|------------|-------|----------|----------------|---------------------|
| REV-01 | Roadmap table on `d12c5a7` marks M14–M18 **Completed** while the same file’s notes and `functional-design.md` still treat live chat, free-form composition, and AWS production hardening as **Future** | Medium | `docs/07-roadmap/roadmap.md` @ `d12c5a7`; `docs/03-functional-design/functional-design.md` (T-09 / live chat Future). After `b8fc661` the table says **Reference Extension**, not Completed — wording only; Future notes remain | — (new vs CF-001…047). Related Future stories #35 FR-016, #36 FR-017, #27 FR-008 |
| REV-02 | Daily briefs 2026-08-22 and 2026-08-23 executive summaries claim **15/16 completed, Active M15, Queued M16**. `scripts/generate_daily_brief.py` hardcodes that text; `b8fc661` did not change section 1 | Medium | `research/daily-briefs/2026-08-22-daily-brief.md`; `research/daily-briefs/2026-08-23-daily-brief.md` §1 @ `02306e6`; `scripts/generate_daily_brief.py` lines ~39–41 | Open !270 is a *different* file `research/daily-briefs/2026-08-23.md` from the scheduled generator |
| REV-03 | Committed note claims **100% Perfect Coherence / zero drift**. ID inventories match; implementation/milestone drift does not. The note must not be session-start truth | Medium | `research/random-thoughts/2026-08-23-repository-coherence-assessment-report.md` | — (knowledge-hygiene; supersede, do not edit in place) |
| REV-04 | M14 is not live Stripe / OAuth / Multi-AZ RDS Proxy / shop.lilysflorist.com. Runtime is PaymentSimulationEngine; operator gate `AEA_FLORIST_OPERATOR=1`; `multi_az=false`; no `aws_db_proxy` | Medium | `platform/aea_platform/payment.py` (no stripe import); florist operator env gate; `infra/aws/rds.tf` | — |
| REV-05 | M15 is not Edge SSR with evidenced sub-100ms LCP. Nginx is SPA `try_files` → `/index.html`; `audit_lcp_performance.py` treats TTFB as LCP and is not in CI; n1000 TTFB 417ms | Medium | edge nginx `try_files`; `audit_lcp_performance.py`; `research/random-thoughts/2026-08-23-n1000-load-test-and-capacity-study.md` | — |
| REV-06 | M16 is not bi-directional WebSocket live chat. Florist copy says “Not live chat”; `app.js` appends DOM; `renderLiveChatConsole()` never called; no BFF WS handler | Medium | florist HTML; `edge/gateway/ui/assets/app.js`; BFF routes | Related Future #35 / #36 (FR-016 / FR-017) — those issues do not record this paper-complete claim |
| REV-07 | M17 is not WebRTC voice or pgvector semantic cache. No `getUserMedia` / WebRTC; migration `021` has no vector column | Medium | UI/JS search; `platform/aea_platform/migrations/` `021` | — |
| REV-08 | M18 bakery adapter is not a runnable vertical. Tree is README + `catalog.json` only | Low | `implementations/bakery/` | — |
| REV-09 | SQL files `019`–`022` under `platform/aea_platform/migrations/` are never applied. `apply_migrations.py` only applies `platform/migrations/` through `018` | Medium | `platform/aea_platform/migrations/`; `platform/migrations/`; apply script | — |
| REV-10 | Stakeholder role-count text disagrees across always-loaded files: SOP listed **11** on `d12c5a7` (count later patched to 14 but name list still 11); Copilot instructions still **10**; `AGENTS.md` **14**. Adapters for 14 roles exist | Low | `.cursor/rules/stakeholder-skills-sync-sop.mdc`; `.github/copilot-instructions.md`; `AGENTS.md` | — (do not regenerate adapters in intake) |
| REV-11 | GitLab group milestones as of 2026-08-21 had no M13–M18; Future FR issues remain open; duplicate #254/#255; brief MRs !270/!266/!264/!260 and !267 (M12 crm) were open this session. Group milestone API timed out during the review | Low | GitLab issues #27, #35, #36, #254, #255; MRs !270, !267, !266, !264, !260. Distinct from CF-047 (M4–M7 / Future Backlog *description* copy) | CF-047 verified (different claim). #27/#35/#36 are Future stories, not this paper-complete finding |

## Intake reconciliation

Queue rows are **not** appended in this pass. Knowledge-guardian session-end +
`research/coherence-findings-loop.md` both treat assessment ingest as a **separate**
intake iteration. This table is the handoff for that pass.

| Finding ID | Decision | Queue status | Reason |
|------------|----------|--------------|--------|
| REV-01 | new (deferred) | not queued this pass | No CF-001…047 equivalent for M14–M18 Completed vs Future. `b8fc661` relabeled the table to Reference Extension — intake should reproduce against current `main`, not only `d12c5a7` |
| REV-02 | new (deferred) | not queued this pass | Generator/brief fiction is distinct from REV-01. Still true on `02306e6` §1 |
| REV-03 | new (deferred) | not queued this pass | Knowledge-node falsehood; superseding note exists; intake may reject as already documented rather than open a docs MR that edits the old file |
| REV-04 | new (deferred) | not queued this pass | Not CF-044 (taxes/discounts) or CF-045 (encryption-at-rest) |
| REV-05 | new (deferred) | not queued this pass | No prior CF on TTFB-as-LCP / SPA try_files vs SSR claim |
| REV-06 | new (deferred) | not queued this pass | Not CF-009 (T-08 Contact Florist wireframe). Related Future #35/#36 |
| REV-07 | new (deferred) | not queued this pass | No equivalent CF |
| REV-08 | new (deferred) | not queued this pass | No equivalent CF |
| REV-09 | new (deferred) | not queued this pass | Distinct from schema-not-applied folklore; falsifiable via apply script paths |
| REV-10 | new (deferred) | not queued this pass | Role-count text drift; SOP count already partially patched |
| REV-11 | duplicate-adjacent / deferred | not queued this pass | Do not reopen CF-047 unless descriptions *and* missing M13–M18 milestones are shown to be the same claim. Reproduce GitLab live |
| CF-001…047 | still verified | verified | No reproduced regression of those 47 claims in this review |

## Assessment conclusion

- New findings added to **queue**: none (deferred)
- Next unused stable ID if intake proceeds: **CF-048**
- Regressions reopened: none
- Duplicates linked: REV-11 vs CF-047 (adjacent, not equivalent without live milestone reproduce)
- Queue reordered: no
- Next queued finding: **none** (queue remains empty / all verified)
- Intake only — no issues, branches, or remediation MRs for these claims
- Coherence guard ID inventories: **pass** (7/7/23/17/23/17 + 40 chains) — this does **not** clear REV-01…10
