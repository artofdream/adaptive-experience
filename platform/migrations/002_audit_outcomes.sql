BEGIN;

ALTER TABLE orchestration.consumed_message
    ADD COLUMN failure_code text,
    ADD COLUMN correlation_id text;

CREATE INDEX consumed_message_session_version_idx
    ON orchestration.consumed_message (session_id, context_version)
    WHERE session_id IS NOT NULL;

INSERT INTO orchestration.schema_migration(version) VALUES (2);
COMMIT;

