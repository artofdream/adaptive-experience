BEGIN;

CREATE SCHEMA IF NOT EXISTS orchestration;

CREATE TABLE orchestration.schema_migration (
    version integer PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE orchestration.experience_session (
    session_id uuid PRIMARY KEY,
    state_schema_version integer NOT NULL CHECK (state_schema_version > 0),
    context_version bigint NOT NULL DEFAULT 0 CHECK (context_version >= 0),
    lifecycle_status text NOT NULL DEFAULT 'active'
        CHECK (lifecycle_status IN ('active', 'completed', 'expired')),
    state jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(state) = 'object'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    expires_at timestamptz NOT NULL,
    CHECK (octet_length(state::text) <= 262144)
);

CREATE INDEX experience_session_expiry_idx
    ON orchestration.experience_session (expires_at)
    WHERE lifecycle_status = 'active';

CREATE TABLE orchestration.experience_invalidation (
    session_id uuid NOT NULL REFERENCES orchestration.experience_session(session_id)
        ON DELETE CASCADE,
    context_version bigint NOT NULL CHECK (context_version > 0),
    projection_key text NOT NULL,
    reason text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (session_id, context_version, projection_key)
);

CREATE TABLE orchestration.outbox_message (
    message_id uuid PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES orchestration.experience_session(session_id),
    context_version bigint NOT NULL CHECK (context_version >= 0),
    topic text NOT NULL CHECK (topic ~ '^[a-z0-9]+([._][a-z0-9]+)*$'),
    aggregate_key text NOT NULL,
    envelope jsonb NOT NULL CHECK (jsonb_typeof(envelope) = 'object'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    next_attempt_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    claimed_by text,
    claimed_until timestamptz,
    published_at timestamptz,
    last_error_code text,
    CHECK ((envelope ->> 'message_id')::uuid = message_id),
    CHECK (envelope ->> 'topic' = topic),
    CHECK ((envelope ->> 'context_version')::bigint = context_version),
    CHECK (octet_length(envelope::text) <= 1048576),
    CHECK ((claimed_by IS NULL) = (claimed_until IS NULL))
);

CREATE INDEX outbox_pending_idx
    ON orchestration.outbox_message (next_attempt_at, created_at)
    WHERE published_at IS NULL;

CREATE TABLE orchestration.consumed_message (
    consumer_group text NOT NULL,
    message_id uuid NOT NULL,
    topic text NOT NULL,
    session_id uuid,
    context_version bigint NOT NULL CHECK (context_version >= 0),
    outcome text NOT NULL CHECK (outcome IN ('applied', 'duplicate', 'stale', 'retry', 'dead_letter')),
    processed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (consumer_group, message_id)
);

CREATE FUNCTION orchestration.claim_outbox(
    p_worker text,
    p_limit integer DEFAULT 100,
    p_lease interval DEFAULT interval '30 seconds'
) RETURNS SETOF orchestration.outbox_message
LANGUAGE sql
AS $$
    UPDATE orchestration.outbox_message AS target
       SET claimed_by = p_worker,
           claimed_until = clock_timestamp() + p_lease,
           attempt_count = target.attempt_count + 1
     WHERE target.message_id IN (
        SELECT candidate.message_id
          FROM orchestration.outbox_message AS candidate
         WHERE candidate.published_at IS NULL
           AND candidate.next_attempt_at <= clock_timestamp()
           AND (candidate.claimed_until IS NULL OR candidate.claimed_until < clock_timestamp())
         ORDER BY candidate.created_at
         FOR UPDATE SKIP LOCKED
         LIMIT p_limit
     )
     RETURNING target.*;
$$;

CREATE FUNCTION orchestration.apply_experience_mutation(
    p_session_id uuid,
    p_expected_context_version bigint,
    p_state_schema_version integer,
    p_state jsonb,
    p_invalidations jsonb,
    p_messages jsonb
) RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    v_new_context_version bigint;
BEGIN
    UPDATE orchestration.experience_session
       SET state_schema_version = p_state_schema_version,
           state = p_state,
           context_version = context_version + 1,
           updated_at = clock_timestamp()
     WHERE session_id = p_session_id
       AND lifecycle_status = 'active'
       AND context_version = p_expected_context_version
     RETURNING context_version INTO v_new_context_version;

    IF v_new_context_version IS NULL THEN
        RAISE EXCEPTION 'stale experience context'
            USING ERRCODE = '40001';
    END IF;

    INSERT INTO orchestration.experience_invalidation
        (session_id, context_version, projection_key, reason)
    SELECT p_session_id,
           v_new_context_version,
           item ->> 'projection_key',
           item ->> 'reason'
      FROM jsonb_array_elements(COALESCE(p_invalidations, '[]'::jsonb)) AS item;

    INSERT INTO orchestration.outbox_message
        (message_id, session_id, context_version, topic, aggregate_key, envelope)
    SELECT (item ->> 'message_id')::uuid,
           p_session_id,
           v_new_context_version,
           item ->> 'topic',
           item ->> 'aggregate_key',
           jsonb_set(item -> 'envelope', '{context_version}', to_jsonb(v_new_context_version))
      FROM jsonb_array_elements(COALESCE(p_messages, '[]'::jsonb)) AS item;

    RETURN v_new_context_version;
END;
$$;

INSERT INTO orchestration.schema_migration(version) VALUES (1);
COMMIT;
