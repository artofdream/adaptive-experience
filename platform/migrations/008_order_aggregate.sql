BEGIN;

-- FR-013 order creation. One order per experience session, assembled from the
-- completed T-04 product decision and T-05 delivery decision. Pre-checkout only:
-- payment, checkout, and confirmation are M5. Recipient PII is not stored here;
-- the delivery snapshot carries only the destination_reference.
CREATE TABLE orchestration.customer_order (
    order_id uuid PRIMARY KEY,
    session_id uuid NOT NULL UNIQUE
        REFERENCES orchestration.experience_session(session_id) ON DELETE CASCADE,
    context_version bigint NOT NULL CHECK (context_version >= 0),
    product jsonb NOT NULL CHECK (jsonb_typeof(product) = 'object'),
    delivery jsonb NOT NULL CHECK (jsonb_typeof(delivery) = 'object'),
    status text NOT NULL DEFAULT 'created'
        CHECK (status IN ('created', 'submitted', 'confirmed', 'cancelled')),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

INSERT INTO orchestration.schema_migration(version) VALUES (8);
COMMIT;
