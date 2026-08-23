-- Milestone M12: Engagement CRM & Occasion Memory (FR-016 / FR-017 / NFR-017)
CREATE SCHEMA IF NOT EXISTS crm;

CREATE TABLE IF NOT EXISTS crm.customer_occasion_memory (
    memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    browser_hash VARCHAR(64) NOT NULL,
    session_id UUID NOT NULL,
    occasion_type VARCHAR(64) NOT NULL,
    event_month INT NOT NULL CHECK (event_month BETWEEN 1 AND 12),
    event_day INT NOT NULL CHECK (event_day BETWEEN 1 AND 31),
    recipient_relation VARCHAR(64) NOT NULL DEFAULT 'other',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT uq_browser_occasion UNIQUE (browser_hash, occasion_type, recipient_relation)
);

CREATE INDEX IF NOT EXISTS idx_crm_browser_hash ON crm.customer_occasion_memory(browser_hash);
CREATE INDEX IF NOT EXISTS idx_crm_event_month_day ON crm.customer_occasion_memory(event_month, event_day);
