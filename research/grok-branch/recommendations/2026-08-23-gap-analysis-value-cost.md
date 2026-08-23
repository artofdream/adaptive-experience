# Gap analysis — value, explanation, implementation cost

> **Workstream:** `grok` (markdown only — manual GitLab promotion)  
> **Date:** 2026-08-23  
> **Basis:** Independent assessment on GitHub mirror of `main` + prior CF-048…053 intake  
> **Cost unit:** engineering effort bands (not currency). 1 unit ≈ half-day focused specialist work including review.

**Bands**

| Band | Effort | Typical shape |
|------|--------|----------------|
| **XS** | ≤ 0.5 unit | Doc/string fix, one file |
| **S** | 0.5–1.5 units | Small script + tests/guards |
| **M** | 2–5 units | Multi-file, careful boundary, one MR |
| **L** | 1–2 weeks | Real product surface (SSR, WebSocket, Stripe live) |
| **XL** | Multi-sprint | Cross-region, full CRM, multi-tenant production |

Costs assume **one finding → one branch → one MR**, Docker integration when code paths change, and no archive ID invention.

---

## 1. Coherence / honesty gaps (highest ROI first)

These do not add product capability; they stop the system from **lying to itself** (briefs, roadmap, scripts). Fixing them protects every later decision.

### G1 — CF-048 Daily-brief hardcoding

| | |
|--|--|
| **Explanation** | `generate_daily_brief.py` prints fixed “15/16 complete” and M15 SSR/sub-100ms claims. Every regen re-publishes unsupported status. Dual brief filenames increase clobber risk. |
| **Value** | Restores trust in the daily memory bus shared by all AI models and humans. Prevents false go/no-go and false “guards + milestones green” narratives. Unblocks honest CF queue prioritization. |
| **Cost** | **S** (~1 unit). Edit one script; optional path-ownership note; no product code. |
| **Risk if skipped** | Compounding coherence debt; assessments keep rediscovering the same High finding. |
| **Promote via** | `recommendations/CF-048-daily-brief-honesty.md` |

### G2 — CF-049 M15 SSR / LCP mislabeling

| | |
|--|--|
| **Explanation** | Roadmap titles M15 “Edge SSR”; audit script sets `lcp_score = t_first_byte`. Reality: Nginx `try_files /index.html` SPA shell + client `app.js`. TTFB ≠ browser LCP. |
| **Value** | Stops performance theater. Clear signal when *real* SSR/hydration work is worth funding. Protects NFR-002/004 reporting integrity. |
| **Cost** | **S** (~1 unit) for honest rename + script label fix. **L** if implementing actual SSR + Web Vitals (separate product decision). |
| **Risk if skipped** | FinOps/perf decisions based on fake LCP; M15 looks “done” while UX remains SPA. |

### G3 — CF-050 Migration runner split (019–022)

| | |
|--|--|
| **Explanation** | Runner globs only `platform/migrations/` (001–018). Reference-extension SQL 019–022 lives under `platform/aea_platform/migrations/` and is never applied by the documented path. Roadmap still cites those schemas as delivered artifacts. |
| **Value** | Single truth for “what schema exists in a fresh environment.” Avoids false confidence on live-chat/stem/cache/tenant isolation. |
| **Cost** | **S–M** (1–2 units): move or dual-root discovery + ordering test; update docs. Does **not** equal shipping WebSocket chat or multi-tenant prod. |
| **Risk if skipped** | Prod/stage drift; “schema delivered” claims without apply path. |

### G4 — CF-051 FR-016 / FR-017 narrative collision

| | |
|--|--|
| **Explanation** | Canonical table: FR-016 reminders, FR-017 engagement analytics, both Future. Prose maps “staff CRM and live chat” to FR-016/017. M12 marked Completed against those IDs; M16 also cites them for staff chat. |
| **Value** | Clear backlog language for PO and implementers; prevents double-counting CRM vs staff chat. |
| **Cost** | **XS–S** (0.5–1 unit): prose + roadmap wording only; no workbook ID change unless sponsor explicitly approves archive edit. |
| **Risk if skipped** | Wrong scope in MRs; Future work sold as done. |

### G5 — CF-052 M14 merchant-domain claim

| | |
|--|--|
| **Explanation** | Roadmap claims merchant domain configuration; Terraform examples/defaults are `aea.artof.link` with pilot exception flags—not a multi-merchant domain model. |
| **Value** | Honest production-readiness story; avoids promising multi-tenant domain isolation that isn’t configured. |
| **Cost** | **XS** (doc/roadmap) or **M–L** if building real multi-domain config (product). |
| **Risk if skipped** | Stakeholders assume multi-merchant go-live readiness. |

### G6 — CF-053 M17 pgvector “Future” vs shipped extension path

| | |
|--|--|
| **Explanation** | Migration 013 + Compose image already enable pgvector; roadmap/Future backlog still say extension remains Future. |
| **Value** | Aligns retrieval ADR story with runtime; avoids re-implementing enablement work. |
| **Cost** | **XS** for wording. Using pgvector for real hybrid retrieval quality is **M–L** (product/RAG work under ADR-014/015). |
| **Risk if skipped** | Duplicate “enable pgvector” tasks; confused RAG roadmap. |

**Coherence subtotal (honesty-only path):** about **4–7 units** if CF-048→053 are fixed as doc/script/runner alignment only—high value per unit.

---

## 2. Product / runtime gaps (capability, not just wording)

These are **not** fixed by coherence MRs. Costs assume thin reference design today → production-usable tomorrow.

### P1 — Real browser performance (true LCP, optional SSR)

| | |
|--|--|
| **Explanation** | Static HTML shell is not session-aware SSR. No reliable Web Vitals pipeline in CI. |
| **Value** | Measurable UX; credible NFR-002/004; better conversion on slow networks. |
| **Cost** | **L**: instrumentation + budgets in CI (**M**); progressive hydration/SSR design (**L**). |
| **Depends on** | Honest CF-049 first so success criteria are real. |

### P2 — Live payments (Stripe) vs PaymentSimulationEngine

| | |
|--|--|
| **Explanation** | Simulation/mock path exists; live Stripe SDK + OAuth2 called Future. |
| **Value** | Real checkout revenue path; FR-019 production meaning. |
| **Cost** | **L** (integration, webhooks, secrets, PCI-aware perimeter, test matrix). |
| **Note** | Do not confuse with M14 “Reference Extension” wording fixes (G5). |

### P3 — Staff live chat / operator CRM (WebSocket + tickets)

| | |
|--|--|
| **Explanation** | SQL 019 + route/UI sketches; Python WebSocket service Future. FR-016/017 are not the right IDs for staff chat (see G4). |
| **Value** | Human escalation beyond thin Contact Florist; operator workflow. |
| **Cost** | **L–XL** (realtime service, auth, occupancy, audit, PII boundary). |
| **Depends on** | CF-050 if schema must actually apply; CF-051 for correct requirement mapping. |

### P4 — Multi-tenant / multi-domain isolation

| | |
|--|--|
| **Explanation** | SQL 022 and bakery adapter are reference-level; cross-region RDS and full tenant isolation remain Future. |
| **Value** | Second industry vertical and hard tenant boundaries. |
| **Cost** | **XL** for production multi-tenant; **M** for honest “reference catalog only” documentation. |

### P5 — Advanced composition / vision / WebRTC

| | |
|--|--|
| **Explanation** | Stem schemas and intent-cache SQL sketched; free-form composition and WebRTC audio remain Future. |
| **Value** | Differentiating florist UX beyond thin T-04 options. |
| **Cost** | **L–XL** depending on vision pipeline vs palette-only co-creation already in M10. |

### P6 — CRM depth beyond zero-PII occasion reminders

| | |
|--|--|
| **Explanation** | `EngagementCrmService` is a real thin slice; full engagement analytics and staff CRM are not. Workbook still Future for FR-016/017. |
| **Value** | Retention and occasion-driven revenue if product unparks Future scope. |
| **Cost** | **M–L** after explicit PO unpark (do not silently promote Future → MVP in workbook). |

---

## 3. Process / platform gaps (smaller residual)

| Gap | Explanation | Value | Cost |
|-----|-------------|-------|------|
| **Daily-brief dual writers** | Session `YYYY-MM-DD.md` vs generator `YYYY-MM-DD-daily-brief.md` | Single memory bus | **XS** with CF-048 |
| **Mirror lag** | GitHub one-way `main` only | N/A if process clear | Process only |
| **Sandbox ≠ full git remote** | Local tree not a pushable clone of GitLab | Use grok-branch MD + manual MR | Process only |
| **Load/perf evidence freshness** | Locust/ASO walks exist in research; continuous prod SLO is separate | Confidence in NFR-003/006 | **M** ongoing |

Mechanical guards are **not** a gap on full `main` (14/14).

---

## 4. Recommended sequencing (value / cost)

```
Phase A — Honesty (do first)
  CF-048 → CF-049 → CF-050 → CF-051 → CF-052 → CF-053
  Cost: ~4–7 units | Value: trust in briefs, roadmap, apply path

Phase B — Product choices (PO go/no-go each)
  Live Stripe | Real LCP/SSR | WebSocket staff chat | Multi-tenant
  Cost: L–XL each | Value: only if strategy funds them

Phase C — Explicit Future unpark
  FR-016/017 depth only with workbook-aware sponsor decision
```

**Do not** spend L/XL product effort to “make the brief true” without Phase A—the brief will still hardcode fantasy until CF-048 lands.

---

## 5. What not to do

- Bundle CF-048…053 into one MR (violates coherence SOP).
- Implement Stripe/WebSocket “so that M14/M16 claims become true” without PO scope and separate issues.
- Invent new FR/US IDs to paper over narrative collisions.
- Treat 14/14 guards as proof of M14–M18 product completion.
- Push delivery work to the GitHub mirror.

---

## 6. Summary table

| ID / theme | Type | Value | Cost (honesty path) | Cost (full product) |
|------------|------|-------|---------------------|---------------------|
| CF-048 Daily brief | Coherence | High | S | — |
| CF-049 M15 LCP/SSR labels | Coherence | High | S | L (real SSR/Vitals) |
| CF-050 Migrations 019–022 | Coherence | High | S–M | — (apply path ≠ feature complete) |
| CF-051 FR-016/017 prose | Coherence | Medium | XS–S | — |
| CF-052 M14 domain claim | Coherence | Medium | XS | M–L (real multi-domain) |
| CF-053 pgvector status | Coherence | Medium | XS | M–L (RAG use) |
| Live Stripe | Product | High if selling | — | L |
| Staff WebSocket chat | Product | Medium–High | — | L–XL |
| Multi-tenant prod | Product | Strategic | — | XL |

**Best near-term investment:** Phase A coherence fixes (~one week of focused guardian/engineer time) before any large product bet that depends on roadmap language being believable.

---

## Promotion

- This file: `research/grok-branch/recommendations/2026-08-23-gap-analysis-value-cost.md`
- Actionable first MR brief remains: `CF-048-daily-brief-honesty.md`
- Formal CF queue updates: manual `@aea-coherence-guardian` intake on GitLab when you promote
