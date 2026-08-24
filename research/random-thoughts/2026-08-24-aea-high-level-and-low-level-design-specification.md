# AEA High-Level Design (HLD) & Low-Level Design (LLD)

> Tags: #aea #architecture #hld #lld

## HLD Overview
AEA is a multi-tier, event-driven adaptive commerce platform.
- Edge Tier: Nginx reverse proxy + SPA assets.
- BFF Tier: FastAPI REST & Starlette WebSockets (/ws/*).
- Domain Tier: Python microservices under platform/aea_platform/.
- Data Tier: PostgreSQL 16 + pgvector HNSW index + MSK Kafka topics.

## LLD Details
- 22 SQL Migrations (001-022).
- Domain Manager Interfaces: LiveChatService, StripePaymentService, SemanticCacheService, TenantIsolationService.

## Related Notes
* [[2026-08-24-24-hour-lessons-learned-retrospective]]
* [[2026-08-24-aea-gaps-vs-reality-reconciliation-and-assessment]]
