BEGIN;

CREATE TABLE orchestration.message_audit (
    message_id uuid NOT NULL,
    stage text NOT NULL CHECK (stage IN ('publication', 'consumption')),
    actor text NOT NULL,
    topic text NOT NULL,
    source text NOT NULL,
    correlation_id text NOT NULL,
    context_version bigint NOT NULL CHECK (context_version >= 0),
    publication_time timestamptz NOT NULL,
    outcome jsonb NOT NULL CHECK (jsonb_typeof(outcome) = 'object'),
    security_context jsonb NOT NULL CHECK (jsonb_typeof(security_context) = 'object'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (message_id, stage, actor),
    CHECK (octet_length(outcome::text) <= 8192),
    CHECK (octet_length(security_context::text) <= 8192)
);

CREATE INDEX message_audit_correlation_idx
    ON orchestration.message_audit (correlation_id, recorded_at);

CREATE FUNCTION orchestration.audit_outbox_insert() RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO orchestration.message_audit
        (message_id, stage, actor, topic, source, correlation_id,
         context_version, publication_time, outcome, security_context)
    VALUES
        (NEW.message_id, 'publication', NEW.envelope ->> 'source', NEW.topic,
         NEW.envelope ->> 'source', NEW.envelope ->> 'correlation_id',
         NEW.context_version, (NEW.envelope ->> 'publication_time')::timestamptz,
         COALESCE(NEW.envelope -> 'outcome', '{}'::jsonb) || '{"status":"queued"}'::jsonb,
         NEW.envelope -> 'security_context');
    RETURN NEW;
END;
$$;

CREATE TRIGGER audit_outbox_insert
AFTER INSERT ON orchestration.outbox_message
FOR EACH ROW EXECUTE FUNCTION orchestration.audit_outbox_insert();

INSERT INTO orchestration.schema_migration(version) VALUES (3);
COMMIT;
