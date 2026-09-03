-- 024_operator_crm_subject_profile.sql
-- Privacy-Preserving Pseudonymous CRM & Ephemeral Fulfillment (ADR-020, ADR-013, NFR-017)

CREATE TABLE IF NOT EXISTS orchestration.subject_profile (
    subject_reference VARCHAR(64) PRIMARY KEY,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    total_orders INTEGER NOT NULL DEFAULT 0,
    lifetime_spend_band VARCHAR(32) NOT NULL DEFAULT 'band_0_50',
    primary_occasion VARCHAR(64),
    preferred_channel VARCHAR(32) DEFAULT 'web',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS orchestration.ephemeral_fulfillment (
    destination_reference UUID PRIMARY KEY,
    encrypted_address BYTEA NOT NULL,
    delivery_phone_hash VARCHAR(64),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (clock_timestamp() + interval '14 days'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX IF NOT EXISTS idx_ephemeral_fulfillment_expiry ON orchestration.ephemeral_fulfillment (expires_at);

INSERT INTO orchestration.schema_migration (version, description)
VALUES (24, '024_operator_crm_subject_profile.sql')
ON CONFLICT (version) DO NOTHING;
