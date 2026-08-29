# Cloud FinOps: Cost Optimization Rationale, Architecture, and Enforcement Protocols

> **Tags**: #aea #second-brain #finops #cost-optimization #architecture #aws #fargate #rds #governance #knowledge-first
> **Captured**: 2026-08-29
> **Author**: @aea-cost-guardian, @aea-knowledge-guardian, @aea-devsecops-platform
> **GitLab Tracker**: Related #282, #286
> **Owners to inherit**: @aea-devsecops-platform, @aea-cost-guardian, @aea-ai-engineer, @aea-project-manager

---

## 1. Executive Summary & Objective

In production and long-running cloud deployments, infrastructure and AI token consumption can rapidly accumulate silent costs if left unconstrained. This knowledge note records the **architectural rationale ("the why")** and the **enforcement mechanisms ("the how")** implemented to achieve predictable, right-sized cloud spend across the Adaptive Experience Architecture (AEA) without compromising performance, reliability, or dual-viewport fidelity.

---

## 2. The Architectural Rationale ("The Why")

### A. AWS ECS Fargate: Graviton (ARM64) Migration
* **The Problem**: Default Fargate task configurations deploy to `X86_64` architecture. In `us-east-1`, x86 Fargate compute costs \$0.04048 per vCPU-hour and \$0.004445 per GB-hour.
* **The Rationale**:
  * AEA microservices (`bff`, `orchestration`, `relay`, `gateway`, `consumer_workspace`, `lily_reference_live_test`, `agent_runner`) run modern interpreted Python 3.12 and FastAPI workloads.
  * AWS Graviton (ARM64) processors provide identical or superior compute throughput for Python bytecode execution with zero architectural friction.
  * ARM64 Fargate pricing is **20% cheaper** (\$0.03238 per vCPU-hour and \$0.003556 per GB-hour), yielding immediate compute savings with zero code modifications.

### B. Amazon RDS PostgreSQL: Pilot Right-Sizing
* **The Problem**: Initial pilot provisioning utilized `db.t4g.medium` (2 vCPU, 4 GB RAM @ \$0.068/hr $\approx$ \$50.59/mo), which was over-provisioned for the pilot phase where transactional TPS rarely exceeds single digits.
* **The Rationale**:
  * Scaling down to `db.t4g.small` (2 vCPU, 2 GB RAM @ \$0.034/hr $\approx$ \$25.29/mo) reduces database compute cost by **50%**.
  * Memory profiling confirms the session property graph, inventory cache, and reorder tables require $< 600\text{MB}$ in active working memory during pilot load.
  * Downscaling is a non-destructive declarative Terraform modification with zero schema drift.

### C. AI & LLM Token Budget Governance (`ADR-016`)
* **The Problem**: High-concurrency integration testing, automated pre-flight guards, and autonomous agent loops can inadvertently trigger massive API bills if directly wired to third-party commercial LLM endpoints (e.g., Claude 3.5 Sonnet or GPT-4o).
* **The Rationale**:
  * Under **ADR-016**, high-throughput load tests and automated CI suites are strictly decoupled from paid token consumption via `AEA_LOAD_TEST_MOCK_AI=1` (`LOAD-003`).
  * Live user queries are proxied through LiteLLM with strict LRU embedding caching, token length truncation, and model tier routing (fast intent classifiers routed to lightweight models; complex synthesis reserved for flagship models).

---

## 3. Enforcement Mechanisms & Operational Protocols ("The How")

```
┌──────────────────────────────┬──────────────────────────────┬──────────────────────────────┐
│ FinOps Dimension             │ Enforcement Mechanism        │ Source of Truth / Artifact   │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ 1. Compute Architecture      │ Declarative runtime_platform │ infra/aws/ecs.tf             │
│                              │ blocks in Terraform          │ (cpu_architecture = "ARM64") │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ 2. Database Sizing           │ Default variable lock in     │ infra/aws/variables.tf       │
│                              │ Terraform configuration      │ (db_instance_class)          │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ 3. Automated Test Mocking    │ Fail-closed mock AI routing  │ ADR-016, platform/seeder.py  │
│                              │ in integration/load scripts  │ (AEA_LOAD_TEST_MOCK_AI=1)    │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ 4. Pre-Flight Verification   │ 14/14 Pre-flight guard suite │ scripts/run_all_guards.py    │
│                              │ verifying secrets & posture  │ scripts/check_secrets_...    │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ 5. Continuous Audit Loop     │ Cadence status tracking &    │ research/daily-briefs/       │
│                              │ monthly FinOps reviews       │ @aea-cost-guardian skill     │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

---

## 4. Run-Rate Benchmark Summary

* **Baseline Pre-Optimization**: $\sim \$329.78/\text{mo}$
* **Optimized Post-Right-Sizing**: $\sim \$282.00/\text{mo}$ (Net monthly savings $\sim \$47.78/\text{mo}$ or $14.5\%$ total infrastructure reduction).

Existing IDs: [[2026-08-29-sprint-coordination-finops-and-ux]], [[2026-08-29-public-voice-pass]], [[2026-08-29-journal-vector-svg-diagrams]], [[2026-08-29-framework-reader-mode-theme-and-a11y]].
