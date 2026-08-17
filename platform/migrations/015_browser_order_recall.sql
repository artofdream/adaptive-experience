BEGIN;

-- M8 #193: last accepted catalog product for this browser. Opaque recall_id
-- only; no login, no customer identity, no purchase-history CRM (FR-016/017).
CREATE TABLE orchestration.browser_order_recall (
    recall_id uuid PRIMARY KEY,
    product_id text NOT NULL CHECK (product_id <> ''),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

ALTER TABLE orchestration.experience_session
    ADD COLUMN recall_id uuid;

CREATE INDEX experience_session_recall_idx
    ON orchestration.experience_session (recall_id)
    WHERE recall_id IS NOT NULL;

INSERT INTO orchestration.schema_migration(version) VALUES (15);
COMMIT;
