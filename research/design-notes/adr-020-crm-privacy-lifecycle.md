# ADR-020 CRM privacy lifecycle (erasure, retention, shredding)

> Companion to [`docs/06-adr/ADR-020-privacy-preserving-crm-and-edge-wallet.md`](../../docs/06-adr/ADR-020-privacy-preserving-crm-and-edge-wallet.md).
> Scope: the zero-PII lifecycle for Layer 1 occasion memory and the Layer 3
> ephemeral fulfillment vault. Non-sponsor-gated; KMS encryption stays gated.

## Why

The zero-PII Engagement CRM (Layer 1) stored occasion memory with no way to
forget it and no retention bound — an incomplete privacy story even without PII.
Layer 3's ephemeral vault (migration 024) had a 14-day `expires_at` column but
nothing shredded expired rows. This note records the lifecycle that closes both.

## Occasion memory (Layer 1)

- **Record** — `POST /api/v1/crm/occasions` → `EngagementCrmService.record_occasion`
  → `crm.customer_occasion_memory` (only `browser_hash`, `occasion_type`,
  `event_month/day`, `recipient_relation`).
- **Read (reminders)** — `GET /api/v1/crm/reminders` → `get_reminders` computes a
  **deterministic** next-occurrence reminder on read. This is a **pull signal**,
  not proactive delivery: there is no FCM/APNs push and the text is a fixed
  template, not "AI-generated" (see ADR-019 for the unshipped push vision). Docs
  and status now state this plainly to avoid overstating FR-016.
- **Erasure (opt-out)** — `EngagementCrmService.forget(browser_hash)` /
  `DELETE /internal/v1/crm/occasions?browser_hash=…` removes all memory for a
  browser (idempotent). Zero-PII customer right-to-forget.
- **Retention** — `purge_expired(retention_days=400)` deletes memory whose
  `updated_at` predates the window (~13 months = one annual cycle + margin).

## Ephemeral fulfillment (Layer 3)

- **Shredding** — `PsycopgCrmStore.purge_expired_fulfillment(now)` deletes
  `orchestration.ephemeral_fulfillment` rows past `expires_at` (14-day default
  from migration 024). This is the retention/shredding half of Layer 3.
- **Still sponsor-gated** — the KMS-encrypted write path that *populates*
  `encrypted_address` at fulfillment time needs cloud KMS + budget and is not
  built. The shredding lifecycle is safe and testable without it.

## Operational job

`platform/scripts/purge_crm_retention.py` runs both purges (occasion retention +
ephemeral shredding) once or on a `--loop` interval.

## Tests

- Unit (`platform/tests/test_crm.py`): forget erases only the target browser and
  is idempotent; `purge_expired` removes stale-but-not-recent memory; validation.
- Integration (`platform/tests/test_postgres_integration.py`): occasion
  erasure + retention purge against Postgres; ephemeral shredding deletes expired
  rows and keeps in-window rows. Migration guards bumped to 25.

## Not in this slice

The pseudonymous subject-profile CRM (`CrmService`, `orchestration.subject_profile`)
still lacks its persistence adapter (`record_crm_order`/`get_crm_profile`) and
order-confirmation/operator wiring — tracked separately as the next CRM slice.
