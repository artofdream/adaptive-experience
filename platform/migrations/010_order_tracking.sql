BEGIN;

-- FR-023 order tracking: add the `completed` terminal status and an orthogonal
-- `delayed` flag. Delay is not a linear status (it can occur at any active stage
-- and resolve), so it is a flag; the displayed authoritative state is `delayed`
-- while set, otherwise the linear status.
ALTER TABLE orchestration.customer_order
    DROP CONSTRAINT customer_order_status_check;
ALTER TABLE orchestration.customer_order
    ADD CONSTRAINT customer_order_status_check
    CHECK (status IN ('created', 'submitted', 'preparing', 'dispatched',
                      'delivered', 'completed', 'confirmed', 'cancelled'));
ALTER TABLE orchestration.customer_order
    ADD COLUMN delayed boolean NOT NULL DEFAULT false;

INSERT INTO orchestration.schema_migration(version) VALUES (10);
COMMIT;
