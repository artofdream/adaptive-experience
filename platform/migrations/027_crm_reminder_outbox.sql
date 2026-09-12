-- 027_crm_reminder_outbox.sql
-- FR-016 / #428: least-data outbound reminder outbox (dry-run only).
-- Categorical occasion fields + copy. No contact columns (no email/phone/push token).
-- Rows stay status=dry_run; send is stubbed fail-closed (not_sent / not_implemented).
-- Cascades when occasion memory is forgotten or retention-purged (NFR-017).

BEGIN;

CREATE TABLE IF NOT EXISTS crm.reminder_outbox (
    outbox_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID NOT NULL REFERENCES crm.customer_occasion_memory(memory_id) ON DELETE CASCADE,
    occasion_year INT NOT NULL CHECK (occasion_year BETWEEN 2000 AND 2100),
    occasion_type VARCHAR(64) NOT NULL,
    recipient_relation VARCHAR(64) NOT NULL,
    days_until_event INT NOT NULL CHECK (days_until_event BETWEEN 0 AND 366),
    reminder_text TEXT NOT NULL,
    copy_source VARCHAR(16) NOT NULL CHECK (copy_source IN ('ai', 'template')),
    status VARCHAR(16) NOT NULL DEFAULT 'dry_run' CHECK (status = 'dry_run'),
    send_disposition VARCHAR(32) NOT NULL DEFAULT 'not_sent'
        CHECK (send_disposition IN ('not_sent', 'not_implemented')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT uq_reminder_outbox_memory_year UNIQUE (memory_id, occasion_year)
);

CREATE INDEX IF NOT EXISTS idx_crm_reminder_outbox_status
    ON crm.reminder_outbox (status, send_disposition, days_until_event);

INSERT INTO orchestration.schema_migration (version)
VALUES (27)
ON CONFLICT (version) DO NOTHING;

COMMIT;
