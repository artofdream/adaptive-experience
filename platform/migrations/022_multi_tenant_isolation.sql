-- Migration 022: Multi-Tenant Schema Partitioning & Data Isolation (GAP-E02)
-- Adds tenant_id partition column and index for multi-brand deployment

BEGIN;

ALTER TABLE IF EXISTS live_chat_tickets
ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(64) DEFAULT 'lilys-florist-primary';

ALTER TABLE IF EXISTS orders_outbox 
ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(64) DEFAULT 'lilys-florist-primary';

CREATE INDEX IF NOT EXISTS idx_live_chat_tickets_tenant ON live_chat_tickets(tenant_id);

INSERT INTO orchestration.schema_migration(version) VALUES (22);
COMMIT;
