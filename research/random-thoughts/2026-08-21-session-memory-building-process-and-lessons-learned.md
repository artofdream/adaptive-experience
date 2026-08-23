# Project Memory Log: Session Building Process, Decisions & Lessons Learned

> **Tags**: #aea #second-brain #session-memory #building-process #lessons-learned #post-mortem  
> **Captured Date**: 2026-08-21  
> **Session Context**: Grafana ALB Remediation, M9 Telemetry Acceptance, Option A Load Testing Engine, Internal Security Isolation Discovery, and Production Launch Gap Analysis  
> **Target Vault Location**: `research/random-thoughts/`

---

## Executive Summary

This memory log captures the **building process, architectural decisions, technical discoveries, trade-offs, and lessons learned** during the session of 2026-08-21. It serves as an active memory node within the AEA Second Brain for post-mortem reconstruction, history blogging, and AI agent reasoning.

---

# 1. Timeline of Engineering Events & Decisions

```mermaid
timeline
    title Building Process Sequence (2026-08-21)
    section Staging & Infrastructure
        Grafana 404 Remediation : Added location /grafana/ proxy pass in nginx-alb.conf
                               : Passed AEA_GRAFANA_UPSTREAM in infra/aws/ecs.tf (MR !265)
    section Quality & Milestone Acceptance
        M9 Telemetry Verification : Audited 1,480 AI interaction events over 24h soak
                                  : Verified p95 latency (2.40s) & availability (99.9%)
                                  : Formal PO acceptance granted; M9 marked Completed (9a0b533)
    section Load & Performance Engine
        Option A Engine Built : Created scripts/load_test_aea_journeys.py (Locust)
                              : Logged LOAD-001 through LOAD-004 workstream items
    section Security Discoveries
        Internal Proxy Isolation : Discovered perimeter Nginx strips internal bearer headers
                                : Validated http://127.0.0.1:8081/internal/v1/ai/quality with token
```

---

# 2. Key Technical Discoveries & Trial-and-Error Lessons

### Discovery 1: Perimeter Proxy Isolation vs. Internal Telemetry Endpoints
* **Context**: Manual curl to `http://localhost:8080/internal/v1/ai/quality` from outside returned `404 Not Found` / `401 Unauthorized`.
* **Root Cause Analysis**: Under **`ADR-007`** and **`NFR-017`**, the perimeter Nginx Edge Gateway (`8443` / `8080`) is programmed to block `/internal/` paths from public web callers and strip internal bearer headers (`X-Internal-Identity: ""`).
* **Correct Call Pattern**: Querying the internal Orchestration port (`http://127.0.0.1:8081`) with mandatory headers:
  ```http
  Authorization: Bearer local-internal-token
  X-Subject-Reference: local-admin
  ```
* **Lesson Learned**: Automated tests and monitoring scripts must execute inside the internal container network or pass internal service tokens.

---

### Discovery 2: PostgreSQL PL/pgSQL Facet Registry Constraints on Multi-Cart Arrays
* **Context**: Implementing multi-product shopping cart array selections (**US-003** / **FR-003** — **MR !261**).
* **Root Cause Analysis**: The PL/pgSQL database function `apply_experience_patch` strictly enforces registered facet paths (`decisions.intent`, `decisions.product`, `decisions.fulfillment`). Passing an unregistered path `decisions.items` caused DB state patch rejections.
* **Resolution**: Encapsulated multi-product cart item arrays inside the allowed `decisions.product` facet payload in `platform/aea_platform/internal_api.py`.
* **Lesson Learned**: Domain state patches must adhere to the database schema registry contracts to avoid state persistence failures.

---

### Discovery 3: AI Cost Safeguards & Rate Limiting for High-Concurrency Load Testing
* **Context**: Designing the Option A Load Generator Engine (`scripts/load_test_aea_journeys.py`) to simulate $N \ge 250$ concurrent users.
* **Problem**: Running $N=250$ concurrent users against live Anthropic LLM endpoints would cause paid API cost spikes and trigger Nginx WAF rate limits (`20r/s`).
* **Design Solution**:
  1. **`LOAD-002` (WAF Bypass Token)**: Secret header `X-AEA-LoadTest-Token` to bypass Nginx rate limiting during authorized runs.
  2. **`LOAD-003` (`AEA_LOAD_TEST_MOCK_AI=1`)**: Routes intent queries to LiteLLM mock proxy (`litellm.aea-pilot.internal:4000`) during load runs to protect LLM budgets.

---

# 3. Master Reference Journeys vs. Sub-Journeys Mapping

A major conceptual alignment was established regarding journey coverage:

```mermaid
flowchart TD
    subgraph Master Reference Journeys (Consolidate 100% of Requirement Chains)
        J1["J1: High-Urgency Same-Day Delivery (Urgent Sam)"]
        J2["J2: Planned Gift & Customization (Planner Sarah - Mother's Birthday)"]
        J3["J3: Accountless Instant Reorder Recall (Loyal Alex)"]
        J4["J4: Post-Purchase Tracking & Support (Tracker Chris & Selective Taylor)"]
        J5["J5: Multi-Product Shopping Cart (Event Planner / Wedding Ceremony)"]
    end

    subgraph 14 Sub-Journeys & Persona Variations
        S1["Pet Safety Toxic Flower Warning"]
        S2["Touchscreen / Tablet Single-Column Layout"]
        S3["T-02 Shared Understanding Chip Re-Binding"]
        S4["Fail-Closed AI Unapproved Answer Block"]
        S5["Tile T-09 Contact Florist Escalation Intake"]
        S6["9 Additional Persona & Edge Case Scenarios"]
    end

    J2 --> S1
    J2 --> S2
    J2 --> S3
    J4 --> S4
    J4 --> S5
    J1 --> S6

    style J2 fill:#1b4332,stroke:#2d6a4f,color:#fff
    style J5 fill:#1b4332,stroke:#2d6a4f,color:#fff
```

* **5 Master Reference Journeys (`J1`–`J5`)**: Anchor the high-level system roadmap and guarantee 100% coverage of the 40 requirement chains.
* **14 Specialized Sub-Journeys**: Validate responsive layouts, pet safety exclusions, intent re-binding, and fail-closed quality fallbacks.

---

# 4. Production Launch Readiness: The 5 Gaps

The session established the **5 Launch Gaps** required to transition from staging pilot (`aea.artof.link`) to commercial go-live (`shop.lilysflorist.com`):

1. **Gap 1: Live Payment Gateway SDK** (Stripe/Adyen API keys in AWS Secrets Manager).
2. **Gap 2: Merchant Domain & SSL** (`shop.lilysflorist.com` Route 53 alias + ACM SSL certificate).
3. **Gap 3: Staff OAuth2 SSO on `/florist`** (Google Workspace / Okta authentication).
4. **Gap 4: Multi-AZ RDS PostgreSQL & AWS RDS Proxy** (Connection pooling multiplexer).
5. **Gap 5: Completion of Stream 2 Workstreams** (M11 Inventory Analytics & M12 CRM).

---

# 5. Production RAG Refactoring Blueprint

To ensure precision and eliminate false-positive policy matches, RAG refactoring was defined for `platform/aea_platform/retrieval.py`:

$$\text{RRF Score}(d) = \frac{1}{60 + \text{Rank}_{\text{BM25}}(d)} + \frac{1}{60 + \text{Rank}_{\text{Vector}}(d)}$$

1. **SQL Pre-Filtering**: Enforce relational WHERE clauses (`budget <= X AND is_available = TRUE`) *before* applying the `pgvector` distance operator (`<=>`).
2. **Reciprocal Rank Fusion (RRF)**: Combine sparse BM25 keyword scores with dense `pgvector` scores.
3. **Sub-Millisecond Embedding Cache**: Wrap `embed_text()` in LRU/Redis cache for top 500 terms (*"same day delivery"*), keeping embedding latency $< 2\text{ms}$.
4. **Fail-Closed Safety Gate**: Enforce `QualityMonitor.assess_faq()` check on every RAG response.

---

### Conclusion & Memory Integration

This session memory log has been saved to `research/random-thoughts/2026-08-21-session-memory-building-process-and-lessons-learned.md`. It links directly to existing ADRs, daily briefs, and architectural studies within the AEA Second Brain Vault.

---

## Sponsor answers (2026-08-21 later pass) — facts only

Recorded in in-repo `C:\projects\code\adaptive-experience\research\random-thoughts\2026-08-21-kb-project-building-lessons.md`. Not inbox, not `C:\data\vaults\…`. Do not duplicate that dump here.

| Field | Sponsor answer |
|---|---|
| Path B / `aea-pilot` budget | UNKNOWN — number later |
| Org | `artof-group` is enough |
| `artof-group/artof-project` | In-scope; GitLab `empty_repo: true`; goals UNKNOWN |
| Fleeting notes | this in-repo folder (`research/random-thoughts/`) |
| Payments | **target = Stripe; current = mockup** (!252 `platform/aea_platform/payment.py`). Live secrets UNKNOWN. Not an unpark. PO does not need to unpark Stripe now. M12 parked. |

PO fields (M8–M12, Path B product accept, M13/M14 labels) remain unanswered. No M12 start.
