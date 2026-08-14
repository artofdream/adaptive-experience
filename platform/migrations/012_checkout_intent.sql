BEGIN;

-- Private checkout payment intent for async authorization (#148).
-- payment_reference stays off the bus (NFR-013); payment consumers load it by
-- draft_order_id when handling order.checkout.requested.
CREATE TABLE orchestration.checkout_intent (
    order_id uuid PRIMARY KEY
        REFERENCES orchestration.customer_order(order_id) ON DELETE CASCADE,
    session_id uuid NOT NULL
        REFERENCES orchestration.experience_session(session_id) ON DELETE CASCADE,
    payment_reference text NOT NULL CHECK (char_length(btrim(payment_reference)) BETWEEN 1 AND 200),
    total numeric(12, 2) NOT NULL CHECK (total > 0),
    correlation_id text NOT NULL,
    subject_reference text NOT NULL,
    context_version bigint NOT NULL CHECK (context_version >= 0),
    decline_code text,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX checkout_intent_session_idx
    ON orchestration.checkout_intent (session_id);

INSERT INTO orchestration.schema_migration(version) VALUES (12);
COMMIT;
