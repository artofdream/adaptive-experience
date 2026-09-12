BEGIN;

-- FR-008 #426: one opaque browser recall may keep several accepted SKUs.
-- Migration 015/017 stored last SKU only (PRIMARY KEY recall_id). The Path B
-- history chooser needs one row per accepted order_id, still least-data, with
-- the 30-day expires_at from 017. Pre-017 rows without order_id stay unreadable.

DELETE FROM orchestration.browser_order_recall WHERE order_id IS NULL;

ALTER TABLE orchestration.browser_order_recall
    DROP CONSTRAINT browser_order_recall_pkey;

ALTER TABLE orchestration.browser_order_recall
    ALTER COLUMN order_id SET NOT NULL;

ALTER TABLE orchestration.browser_order_recall
    ADD PRIMARY KEY (recall_id, order_id);

CREATE INDEX IF NOT EXISTS browser_order_recall_recent_idx
    ON orchestration.browser_order_recall (recall_id, updated_at DESC)
    WHERE expires_at IS NOT NULL;

INSERT INTO orchestration.schema_migration(version) VALUES (27);
COMMIT;
