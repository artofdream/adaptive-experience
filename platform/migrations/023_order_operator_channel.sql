BEGIN;

-- Least-data staff-list channel (#376). Allowlisted X-AEA-Client / aea_client
-- persisted on order create. Observability only — not an auth boundary.
-- Null remains valid for orders created before this column existed.
ALTER TABLE orchestration.customer_order
    ADD COLUMN aea_client text
        CHECK (aea_client IS NULL OR aea_client IN ('web', 'companion-android', 'unknown'));

INSERT INTO orchestration.schema_migration(version) VALUES (23);
COMMIT;
