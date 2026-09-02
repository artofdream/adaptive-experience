# Adaptive Experience Architecture (AEA): DevOps & Architecture Assessment Report

#aea #aea/devops #aea/architecture #aea/report

**Date:** 2026-09-02  
**Author:** `@aea-devsecops-platform` & `@aea-cost-guardian`  
**Repository:** `artof-group/adaptive-experience-architecture`  
**Target Scope:** Platform, Edge, Cloud IaC (AWS Path B), CI/CD, Mobile Companion, and Developer Experience  
**Related Documents:** [[2026-09-02-framework-prove-value-kpis-checklist]] · [[2026-09-02-session-handover-cloud-agents-local-cts-ai]]

---

## 1. Executive Topology & Architecture Overview

The **Adaptive Experience Architecture (AEA)** operates as a **modular monolith with an external event broker**, fronted by a reverse-proxy gateway and a dedicated Backend-for-Frontend (BFF):

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 EDGE PERIMETER (ADR-007)                               │
│                                                                                        │
│   [ Web Browser ]              [ Android Companion ]           [ Operator Portal ]     │
│   (Sub-100ms LCP)              (Jetpack Compose M3)            (T-03 / Staff Queue)    │
│          │                               │                               │             │
│          └───────────────────────┬───────┴───────────────────────────────┘             │
│                                  ▼                                                     │
│                    [ Edge Reverse Proxy / Gateway ]                                    │
│                    • Rate limiting & Origin validation                                 │
│                    • Strips internal identity headers                                  │
│                    • __Host- session cookie management                                 │
│                                  │                                                     │
│                                  ▼                                                     │
│                    [ Edge BFF (aea_bff: Fastify/Py) ]                                  │
│                    • Pure presentation adapter                                         │
│                    • NO direct DB or Kafka imports                                     │
└──────────────────────────────────┬─────────────────────────────────────────────────────┘
                                   │ Internal REST / Zero-PII Contracts
                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                PLATFORM FOUNDATION                                     │
│                                                                                        │
│                    [ Orchestration / Core Services ]                                   │
│                    • Order state machine (ADR-013)                                     │
│                    • Shared understanding resolution                                   │
│                    • Inventory availability engine                                     │
│                                  │                                                     │
│                 ┌────────────────┴────────────────┐                                    │
│                 ▼                                 ▼                                    │
│     [ Amazon RDS PostgreSQL 16 ]       [ Amazon MSK Kafka ]                            │
│     • KMS storage encryption           • TLS + SASL/SCRAM in Prod                      │
│     • Read/Write connection pool       • PayloadPrivacyGuard topics                    │
│     • Idempotent migrations            • Zero-PII message contracts                    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural & DevOps Strengths

| Strength Dimension | Architectural Mechanism | Concrete Evidence & Value |
|---|---|---|
| **1. Quality Guard Railing** | 14 automated pre-flight quality guards (`scripts/run_all_guards.py`) | Runs in under 15 seconds locally and in CI. Enforces 100% requirement traceability (7/23 BG/US, 17/40 FR/NFR), topic schema integrity (`check_topic_schemas.py`), secrets posture (`check_secrets_posture.py`), and 6-way stakeholder skill synchronization across AI assistants. |
| **2. Zero-PII & Privacy by Design** | Strict tokenized payload contracts (`ADR-013`, `NFR-017`, `PayloadPrivacyGuard`) | No personal customer identifiable information (PII) or payment PAN enters event topics or application logs. All deliveries reference tokenized destination IDs (`Ref# LILY-PARIS-01`). |
| **3. Dual-Path Execution Model** | Path A (Local Docker Compose) vs Path B (AWS Cloud IaC) | Path A enables a fast, zero-cloud-cost developer inner loop with mock adapters. Path B (`infra/aws/`) provides production-grade ECS Fargate, RDS PostgreSQL, MSK Kafka, and ACM TLS. |
| **4. Cloud-Native CI/CD Automation** | GitLab CI + AWS OIDC AssumeRole | Zero static AWS access keys stored in CI variables. GitLab CI builds Docker images directly to Amazon ECR, deploys ECS services with health checks, and uploads signed Android release AABs to Google Play internal tracks. |
| **5. Cross-Client Parity** | Web Gateway + Android Jetpack Compose Companion | Uniform state transitions (Need &rarr; Budget &rarr; Pick &rarr; Pay &rarr; Tracking) shared across Web and Mobile with strict contract parity verified by automated probes (`scripts/probe_companion_bff_parity.py`). |

---

## 3. Gaps, Weaknesses & Technical Debt

### A. Developer Inner Loop & Toolchain Drift
- **Issue:** Local developer environments running Java 17 fail during local `./gradlew assembleDebug` because the Android client requires Java 21 (`compileSdk 36`).
- **Impact:** Developers without local JDK 21 must rely on downloading artifacts from GitLab CI or switching environments manually.

### B. Database Migration Deployment Orchestration
- **Issue:** While migrations in `platform/scripts/apply_migrations.py` are idempotent, they are decoupled from the automated ECS service update in `.gitlab-ci.yml`.
- **Impact:** Risk of deploying new application code before required PostgreSQL schema changes are applied.

### C. Kafka Security Protocol Parity (Plaintext vs SASL)
- **Issue:** Local Compose uses plaintext Kafka (`broker:9092`), while AWS MSK uses TLS + SASL/SCRAM authentication.
- **Impact:** Integration tests executed locally do not validate SASL authentication handshakes or credential rotation mechanics.

### D. Distributed Tracing & APM Visibility
- **Issue:** Structured JSON logging is streamed to CloudWatch, but distributed W3C TraceContext headers (`traceparent`) are not ubiquitously propagated across the Gateway &rarr; BFF &rarr; Platform &rarr; Kafka hops.
- **Impact:** Troubleshooting cross-service latency spikes requires manual correlation across multiple CloudWatch log streams.

---

## 4. Actionable DevOps Roadmap & Improvements

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              PRIORITIZED DEVOPS ROADMAP                                │
├───────────────────┬────────────────────────────────────────────────────────────────────┤
│ Priority          │ Action Item & Implementation Plan                                  │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ P1 (Immediate)    │ Containerized Local Build Wrapper:                                 │
│                   │ • Provide `docker run --rm -v $(pwd):/app cimg/android:2024.04 ...` │
│                   │   script so local builds succeed instantly on any developer OS.    │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ P1 (Deploy Safety)│ Automated ECS Pre-Deploy Migration Task:                           │
│                   │ • Add an `aws ecs run-task` migration runner in `.gitlab-ci.yml`   │
│                   │   before `aws ecs update-service` to guarantee schema currency.    │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ P2 (Observability)│ OpenTelemetry W3C TraceContext Ingestion:                          │
│                   │ • Inject `traceparent` at Edge Gateway; pass via HTTP and Kafka    │
│                   │   headers for unified trace graphs.                                │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ P2 (Parity)       │ Local SASL Emulation Compose Profile:                              │
│                   │ • Add `docker-compose.sasl.yml` to test MSK authentication flows   │
│                   │   in pre-flight integration test suites.                           │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ P3 (FinOps)       │ ECS Fargate Right-Sizing & MSK Serverless:                         │
│                   │ • Right-size BFF to 0.25 vCPU / 0.5 GB and Platform to 0.5 vCPU;   │
│                   │   enforce CloudWatch CPU/Memory alarms under ADR-016 spend caps.   │
└───────────────────┴────────────────────────────────────────────────────────────────────┘
```
