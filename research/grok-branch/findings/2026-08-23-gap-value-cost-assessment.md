# Gap assessment — value, explanations, implementation cost

> **Tags:** #aea #gaps #value #cost #grok #manual-promotion  
> **Date:** 2026-08-23  
> **Basis:** Full-tree guards 14/14; workbook coherence pass; CF-048…053 evidence; roadmap M0–M18  
> **Workstream:** `research/grok-branch/` — promote to GitLab manually  
> **Discipline:** One finding → one issue → one branch → one MR when implemented on GitLab

## How to read this note

| Term | Meaning here |
|------|----------------|
| **Gap** | Documented or claimed capability that is missing, thin, mislabeled, or incoherent with evidence |
| **Value** | Why closing it matters (trust, risk, velocity, product) |
| **Cost** | Relative effort: **S** (&lt;0.5 day), **M** (0.5–2 days), **L** (3–10 days), **XL** (multi-week / product decision) |
| **Type** | **Coherence** (honesty of claims) vs **Product** (new capability) vs **Platform** (ops/security) |

Costs assume one senior engineer familiar with the repo, focused MR, guards green. They do **not** include multi-region production hardening.

---

## 1. Executive summary

The repository is **mechanically healthy** (14/14 guards, coherent ID model, real platform/edge code, portable 14-role skills). The dominant gap class is **delivery-claim honesty**: publishers and roadmap language overstate what is shipped (SSR, LCP, migration apply path, merchant domain, pgvector “Future”, FR-016/017 semantics).

Closing **coherence gaps first** is high value / low cost: restores trust in daily briefs and milestone status without building new product features. **Product gaps** (live Stripe, WebSocket chat, real SSR, cross-region) are high cost and should stay explicitly Future unless product prioritizes them.

**Recommended sequence:** CF-048 → CF-049 → CF-050 → CF-051 → CF-052/053 → only then optional product XL items.

---

## 2. Coherence gaps (fix claims and wiring)

### G1 — CF-048: Daily brief hardcodes milestone/performance claims

| | |
|--|--|
| **Explanation** | `scripts/generate_daily_brief.py` writes static “15/16 complete” and M15 SSR/sub-100ms text. Regeneration overwrites honest status. Dual brief filenames add clobber risk. |
| **Value** | High — every stakeholder and cross-model session trusts the daily brief as shared memory. False completion claims poison planning and external assessments. |
| **Cost** | **S–M** (0.5–1 day): strip hardcodes; derive guards from runner; neutral M15 wording; document canonical brief path. |
| **Risk if ignored** | Continuous coherence debt; CF queue and assessments keep re-finding the same issue. |
| **Promotion** | `recommendations/CF-048-daily-brief-honesty.md` |

### G2 — CF-049: M15 “SSR” and TTFB-as-LCP

| | |
|--|--|
| **Explanation** | Edge serves static SPA (`try_files /index.html`). Audit script measures TTFB and labels it “estimated LCP”. Roadmap title implies server-rendered progressive hydration that is not implemented. |
| **Value** | High for performance governance — wrong metric trains the team on the wrong optimization target and misleads FinOps/UX decisions. |
| **Cost** | **S–M**: rename roadmap/script language; separate TTFB from LCP; optional later **L–XL** for real SSR/hydration + browser Web Vitals. |
| **Split** | Honesty fix = S–M (do now). Real SSR product = XL (product decision). |

### G3 — CF-050: Migrations 019–022 outside apply runner

| | |
|--|--|
| **Explanation** | `apply_migrations.py` only globs `platform/migrations/`. Files 019–022 live under `platform/aea_platform/migrations/`, so documented apply path cannot apply them. Roadmap still cites related schemas as reference-extension deliverables. |
| **Value** | High operational — “schema delivered” without apply path = broken envs, false confidence in M16–M18 artifacts. |
| **Cost** | **M**: single root or dual-root discovery with ordered apply + test that 019–022 are visible; update docs. Not the same as shipping live chat product. |
| **Risk if ignored** | Drift between Compose/dev and any env that only runs the documented script. |

### G4 — CF-051: FR-016 / FR-017 semantic collision

| | |
|--|--|
| **Explanation** | Canonical rows: FR-016 = occasion reminders, FR-017 = engagement analytics, both **Future** in workbook. Prose says “staff CRM and live chat remain out of scope (FR-016 / FR-017)”. M12 marked Completed against those IDs; M16 also cites them for staff chat. |
| **Value** | Medium–High for requirements integrity — wrong ID mapping breaks traceability and confuses PO/acceptance. |
| **Cost** | **S–M**: prose + roadmap wording only; no workbook ID invention. Align M12 “thin CRM” language with Future scope note. |

### G5 — CF-052: M14 merchant-domain claim

| | |
|--|--|
| **Explanation** | Terraform examples/defaults use `aea.artof.link`. Pilot exceptions exist; multi-merchant Lily domain config is not represented as claimed. |
| **Value** | Medium — production go-live narrative accuracy; FinOps/domain planning. |
| **Cost** | **S**: correct roadmap text; or **M–L** if product wants real multi-domain config implemented. |

### G6 — CF-053: M17 pgvector “Future” vs migration 013

| | |
|--|--|
| **Explanation** | `013_retrieval_pgvector.sql` + Compose `pgvector/pgvector:pg16` already enable the extension. Roadmap/Future backlog still list “pgvector extension remain Future”. |
| **Value** | Medium — avoids re-work and false “not started” planning for retrieval/RAG. |
| **Cost** | **S**: status wording only. Full hybrid retrieval product depth remains separate (**L–XL**). |

---

## 3. Product / capability gaps (intentionally Future or thin)

These are **not** fixed by coherence MRs. Cost is higher; value depends on product priority.

| Gap | Explanation | Value if closed | Cost | Notes |
|-----|-------------|-----------------|------|--------|
| **Live Stripe + real payment** | PaymentSimulationEngine / mock only; live SDK Future | Required for real checkout revenue path | **L–XL** | Compliance, secrets, webhooks, PCI-aware design |
| **Staff live chat (WebSocket)** | Schema/route/UI thin; Python WS Future | Operator efficiency | **L–XL** | Realtime, auth, multi-tenant isolation (022) |
| **True Edge SSR / progressive hydration** | Static shell today | Perceived performance, SEO if needed | **L–XL** | Architecture change; measure real LCP in browser |
| **WebRTC / voice** | Future backlog | Differentiated UX | **XL** | Media, privacy, device matrix |
| **Cross-region RDS** | Future | Resilience / latency | **XL** | Ops, failover, data residency |
| **Full free-form bouquet composition** | Thin T-04 options delivered; free-form Future | Merchandising depth | **L** | Inventory + pricing rules |
| **Multi-tenant / multi-domain beyond pilot** | SQL 022 + bakery catalog thin | Second vertical / SaaS shape | **L–XL** | Tenancy model, domain routing, isolation tests |

**Value framing:** Coherence fixes protect the *signal* used by all agents and humans. Product XL items expand *capability*. Mixing them in one MR is forbidden by SOP and inflates risk.

---

## 4. Platform / process gaps (secondary)

| Gap | Explanation | Value | Cost |
|-----|-------------|-------|------|
| Daily-brief dual writers | `YYYY-MM-DD.md` vs `*-daily-brief.md` | Avoid clobber / MR collisions | **S** (with CF-048) |
| Mirror lag (GitHub ← GitLab) | One-way `main` only | Awareness only | **—** (process) |
| Real browser LCP in CI | Not measured today | Performance gate quality | **M** after CF-049 honesty |
| Integration tests in constrained sandboxes | Env-dependent skips in unit discovery | Confidence in Docker-before-MR | **M** (CI/runners) |

---

## 5. Value vs cost matrix (priority)

```
High value │  G1 CF-048 ●     G2 CF-049 honesty ●     G3 CF-050 ●
           │  G4 CF-051 ○
           │
Med value  │  G5 CF-052 ○     G6 CF-053 ○     browser LCP gate ○
           │
Lower now  │  live Stripe ■   WebSocket chat ■   real SSR ■   multi-region ■
           └──────────────────────────────────────────────────────────
              Cost S–M                    Cost L–XL
```

- **●** = do next (coherence)  
- **○** = soon after, still coherence  
- **■** = product backlog; explicit Future unless PO prioritizes  

**ROI:** S–M coherence work yields disproportionate trust and planning accuracy. XL product work should be gated by PO go/no-go, not by coherence guardian alone.

---

## 6. Suggested implementation waves (GitLab, manual)

| Wave | Items | Combined cost | Outcome |
|------|--------|---------------|---------|
| **W1** | CF-048 | S–M | Honest briefs; shared memory trustworthy |
| **W2** | CF-049 honesty (not full SSR) | S–M | Correct performance language |
| **W3** | CF-050 | M | Migrations actually applicable |
| **W4** | CF-051, CF-052, CF-053 | S–M each | Roadmap/requirements narrative aligned |
| **W5+** | Product XL backlog | L–XL each | Only with PO prioritization |

Each wave = separate issue/branch/MR. Do not batch W1–W4 into one MR.

---

## 7. What not to spend on yet

- Replacing thin M8–M12 services that already match “thin / workbook stays Future” intent, unless PO expands scope  
- Building SSR solely to satisfy a misnamed milestone title — rename first (W2), build later if product wants it  
- Inventing new FR/US IDs to paper over narrative collisions — fix prose (W4)  

---

## 8. Bottom line

| Question | Answer |
|----------|--------|
| Is the foundation real? | **Yes** — platform, edge, guards, skills, canonical model |
| What hurts most today? | **Over-claiming** in briefs and milestone language |
| Best next spend? | **CF-048** then CF-049 honesty and CF-050 (**S–M**, high value) |
| When to spend XL? | After claims are honest and PO prioritizes revenue, operators, or true SSR |

This note is **not** merged truth until promoted via GitLab. Related actionable brief: `../recommendations/CF-048-daily-brief-honesty.md`.
