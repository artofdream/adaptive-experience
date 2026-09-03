-- 025_crm_retention_indexes.sql
-- Privacy lifecycle for the zero-PII CRM (ADR-020 / NFR-017): support efficient
-- retention purges of occasion memory and pseudonymous subject profiles. Erasure
-- (forget by browser_hash / subject_reference) and time-based purge are DELETEs;
-- these indexes keep the purge scans cheap. The ephemeral fulfillment vault
-- already has idx_ephemeral_fulfillment_expiry from migration 024.
BEGIN;

CREATE INDEX IF NOT EXISTS idx_crm_updated_at
    ON crm.customer_occasion_memory (updated_at);

CREATE INDEX IF NOT EXISTS idx_subject_profile_last_seen
    ON orchestration.subject_profile (last_seen_at);

INSERT INTO orchestration.schema_migration (version)
VALUES (25)
ON CONFLICT (version) DO NOTHING;

COMMIT;
