BEGIN;

-- FR-015 order status updates: preparation, dispatch, delivery. Extend the
-- customer_order status lifecycle to the authoritative fulfillment statuses.
ALTER TABLE orchestration.customer_order
    DROP CONSTRAINT customer_order_status_check;
ALTER TABLE orchestration.customer_order
    ADD CONSTRAINT customer_order_status_check
    CHECK (status IN ('created', 'submitted', 'preparing', 'dispatched',
                      'delivered', 'confirmed', 'cancelled'));

INSERT INTO orchestration.schema_migration(version) VALUES (9);
COMMIT;
