-- 026_crm_lifetime_spend.sql
-- Cumulative lifetime spend total for the pseudonymous subject profile (ADR-020, NFR-017).
-- Stored as integer cents so the lifetime_spend_band is computed from the running
-- total across orders rather than the most recent single order. Still zero-PII:
-- no names, addresses, or payment identifiers are recorded here.

ALTER TABLE orchestration.subject_profile
    ADD COLUMN IF NOT EXISTS lifetime_spend_cents BIGINT NOT NULL DEFAULT 0;

INSERT INTO orchestration.schema_migration (version)
VALUES (26)
ON CONFLICT (version) DO NOTHING;
