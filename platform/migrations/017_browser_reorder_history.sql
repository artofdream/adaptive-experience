BEGIN;

-- FR-008 M8 reorder history remains owned by the opaque browser recall ID.
-- Keep only the accepted order reference, catalog product, and expiry; historical
-- delivery, recipient, options, card message, payment, and other PII are excluded.
ALTER TABLE orchestration.browser_order_recall
    ADD COLUMN order_id uuid
        REFERENCES orchestration.customer_order(order_id) ON DELETE CASCADE,
    ADD COLUMN expires_at timestamptz;

-- Rows created by the earlier thin hint did not prove an accepted order and
-- therefore remain unreadable until a later governed checkout refreshes them.
CREATE INDEX browser_order_recall_active_idx
    ON orchestration.browser_order_recall (recall_id, expires_at)
    WHERE order_id IS NOT NULL AND expires_at IS NOT NULL;

INSERT INTO orchestration.schema_migration(version) VALUES (17);
COMMIT;
