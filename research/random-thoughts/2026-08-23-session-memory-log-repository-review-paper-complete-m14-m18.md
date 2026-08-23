# Session Memory Log: Repository Review — M14–M18 Paper-Complete (Not Shipped)

> **Tags**: #aea #session-memory #kt #knowledge-transfer #second-brain #coherence #paper-complete #m14 #m15 #m16 #m17 #m18
> **Captured**: 2026-08-23
> **Role Context**: @aea-knowledge-guardian (multi-model session-end protocol)
> **Assessed commit**: `d12c5a7` on `main` (facts verified there)
> **Later `main` at write time**: `02306e6` (roadmap wording + a 94/100 note landed after the review; they do **not** ship M14–M18)

---

## SUPERSEDES

**This note SUPERSEDES [[2026-08-23-repository-coherence-assessment-report]].**

That committed report claims **“100.0% Perfect Coherence / zero drift”**. Treat it as **false** for session-start. Workbook vs `docs/` **ID inventories** matching (7 BG, 7 EP, 23 US, 17 NFR-US, 23 FR, 17 NFR, 40 chains) is real. Milestone-shipped and “zero drift” claims are not.

Also do **not** treat these as evidence that M14–M18 shipped:

- [[2026-08-23-session-memory-log-m15-m18-execution-and-mr269-merge]] — KT log that describes live WebSocket chat, WebRTC, pgvector, and bakery as delivered.
- [[2026-08-23-m15-m16-milestone-completion-and-live-chat-architecture]] — architecture study that claims 16/16 complete.
- [[2026-08-23-comprehensive-aea-repository-assessment]] — later 94/100 note on `b8fc661`. Useful as a softening of “Completed”, but it still treats sub-100ms LCP and M16 SQL/nginx/DOM as production-ready / thin-delivered. The falsifiable claims below override that softness.

Canonical intake record (no CF-NNN assigned this pass):
[research/assessments/2026-08-23-repository-review-paper-complete-m14-m18.md](../assessments/2026-08-23-repository-review-paper-complete-m14-m18.md)

---

## Why this node exists

A 2026-08-23 repository review found the **MVP foundation healthy** and **M14–M18 “Completed” claims paper-complete**. The review lived in chat + a Cursor canvas. Other models (Cursor, Codex, Claude, Copilot, Gemini, Grok) do not see the canvas. They **will** see this file, the daily brief, and the assessment under `research/`.

This is knowledge extraction only. **No product remediation. No CF queue rows. No merge.**

---

## What is healthy (`d12c5a7`)

- **14/14** pre-flight guards pass (`python scripts/run_all_guards.py`).
- Workbook vs published `docs/` ID inventories match: 7 BG, 7 EP, 23 US, 17 NFR-US, 23 FR, 17 NFR, 40 mapping chains.
- CF-001…047 are all `verified`; **none queued**.
- Thin real platform code exists: `reorder.py`, `quality.py`, `selection.py`, `forecast.py`, `crm.py`, payment **simulation**.
- 14 stakeholder skills exist with 6-way adapters (Cursor / Codex / Claude / Copilot / Gemini / Grok).

---

## Paper / contradictions (verified on `d12c5a7`)

### Docs vs runtime

- Roadmap table on `d12c5a7` marked **M14–M18 Completed**. Same file notes + `docs/03-functional-design/functional-design.md` still say live chat / free-form composition / AWS remain **Future**.
- After `b8fc661`, the roadmap table says **Reference Extension** instead of Completed. That is a wording change, not a ship. Functional-design Future statements remain. Do not treat the relabel as M14–M18 delivered.

### Daily briefs reprint fiction

- `research/daily-briefs/2026-08-22-daily-brief.md` and `research/daily-briefs/2026-08-23-daily-brief.md` both said **15/16 · Active M15 · Queued M16**.
- `scripts/generate_daily_brief.py` **hardcodes** that executive summary. `b8fc661` updated the stakeholder matrix template only; **section 1 of the generator still prints 15/16**. Do **not** run the generator as-is or it will overwrite an honest brief.

### M14 Production Go-Live

- Runtime is `PaymentSimulationEngine`; no `stripe` import.
- Operator gate is `AEA_FLORIST_OPERATOR=1`, not OAuth2 SSO.
- `infra/aws/rds.tf` has `multi_az = false`; no `aws_db_proxy`.
- No `shop.lilysflorist.com` merchant domain.

### M15 Edge SSR / LCP

- Nginx serves SPA `try_files` → `/index.html` only (not session-state HTML pre-render).
- `audit_lcp_performance.py` treats **TTFB as LCP** and is **not in CI**.
- n1000 study TTFB **417ms** ([[2026-08-23-n1000-load-test-and-capacity-study]]). Sub-100ms LCP is not evidenced.

### M16 Staff live chat

- Florist UI copy: **“Not live chat”**.
- `app.js` chat appends DOM; no WebSocket.
- `renderLiveChatConsole()` is never called.
- No BFF WebSocket handler.

### M17 Vision / composition

- No WebRTC / `getUserMedia`.
- Migration `021` has **no vector column**.

### M18 Bakery / multi-tenant

- Bakery vertical is **README + `catalog.json` only**.

### Migrations never applied

- Files `019`–`022` live under `platform/aea_platform/migrations/`.
- `apply_migrations.py` only applies `platform/migrations/` through **018**. Those four files are never applied.

### Role-count drift (docs, not adapters)

- SOP `.cursor/rules/stakeholder-skills-sync-sop.mdc`: said **11** roles on `d12c5a7`; `b8fc661` changed the count to **14** but the name list still enumerates **11**.
- `.github/copilot-instructions.md` still says **10** roles.
- `AGENTS.md` says **14**.
- Do not regenerate adapters in this pass.

### GitLab (live this session)

- Open: !270 (scheduled 2026-08-23 brief, **different file** `research/daily-briefs/2026-08-23.md`, base behind `main`), !267 (M12 crm).
- Stale brief MRs: !266 / !264 / !260.
- Future issues still open: #27 FR-008, #35 FR-016, #36 FR-017.
- Duplicate issues #254 / #255.
- Group milestone API timed out this session; 2026-08-21 check had **no M13–M18** group milestones.

---

## Decisions & trade-offs this session

1. **Persist, do not remediate.** Other tools must be able to run their own assessments. Un-completing the roadmap, implementing Stripe/SSR/chat, or queuing CF-048+ here would mix knowledge handoff with product work.
2. **Do not overwrite the false 100% report in place.** Supersede it from this node + the daily brief so git history still shows what was claimed.
3. **Do not reuse MR !270.** It is a CI `daily-brief-generate` MR on an older `main`, writing `2026-08-23.md` (no `-daily-brief` suffix). Mixing this review into that MR would collide with the hardcoded generator output.
4. **CF intake deferred.** Assessment file uses local `REV-*` IDs. Next unused stable ID is **CF-048**. Dedicated `@aea-coherence-guardian` intake should assign/reuse after searching CF-001…047 (already searched: no equivalent queued/verified row covers paper-complete M14–M18).

---

## Lesson for later sessions

ID-inventory coherence (workbook ↔ docs) is **not** the same as implementation coherence (roadmap “Completed” ↔ code). A 14/14 guard pass can coexist with paper milestones. If a note says 100% coherence, ask which layer: IDs, guards, or shipped runtime.

---

## Related Second Brain Notes

- [[2026-08-23-repository-coherence-assessment-report]] — **SUPERSEDED**; ID inventories only.
- [[2026-08-23-comprehensive-aea-repository-assessment]] — later 94/100 softening; still over-credits LCP and M16 stubs.
- [[2026-08-23-session-memory-log-m15-m18-execution-and-mr269-merge]] — do not use as ship evidence.
- [[2026-08-23-m15-m16-milestone-completion-and-live-chat-architecture]] — do not use as ship evidence.
- [[2026-08-23-n1000-load-test-and-capacity-study]] — TTFB 417ms evidence against sub-100ms LCP.
- [[2026-08-21-session-memory-building-process-and-lessons-learned]] — prior KT format.
