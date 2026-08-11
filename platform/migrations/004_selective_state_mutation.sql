BEGIN;

CREATE TABLE orchestration.projection_dependency (
    state_facet text NOT NULL,
    projection_key text NOT NULL,
    reason text NOT NULL,
    PRIMARY KEY (state_facet, projection_key)
);

INSERT INTO orchestration.projection_dependency(state_facet, projection_key, reason) VALUES
    ('shared_understanding.occasion', 'recommendations', 'intent_changed'),
    ('shared_understanding.budget', 'recommendations', 'intent_changed'),
    ('shared_understanding.budget', 'order_summary', 'intent_changed'),
    ('shared_understanding.recipient', 'recommendations', 'intent_changed'),
    ('shared_understanding.recipient', 'delivery', 'intent_changed'),
    ('shared_understanding.style', 'recommendations', 'intent_changed'),
    ('shared_understanding.timing', 'recommendations', 'intent_changed'),
    ('shared_understanding.timing', 'delivery', 'intent_changed'),
    ('decisions.product', 'customization', 'product_changed'),
    ('decisions.product', 'delivery', 'product_changed'),
    ('decisions.product', 'order_summary', 'product_changed'),
    ('decisions.customization', 'order_summary', 'customization_changed'),
    ('decisions.delivery', 'order_summary', 'delivery_changed');

CREATE FUNCTION orchestration.jsonb_deep_merge(p_current jsonb, p_patch jsonb)
RETURNS jsonb
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT COALESCE(jsonb_object_agg(
        COALESCE(current_item.key, patch_item.key),
        CASE
            WHEN jsonb_typeof(current_item.value) = 'object'
             AND jsonb_typeof(patch_item.value) = 'object'
                THEN orchestration.jsonb_deep_merge(current_item.value, patch_item.value)
            WHEN patch_item.key IS NOT NULL THEN patch_item.value
            ELSE current_item.value
        END
    ), '{}'::jsonb)
    FROM jsonb_each(p_current) AS current_item
    FULL JOIN jsonb_each(p_patch) AS patch_item USING (key);
$$;

CREATE FUNCTION orchestration.apply_experience_patch(
    p_session_id uuid,
    p_expected_context_version bigint,
    p_state_schema_version integer,
    p_patch jsonb,
    p_changed_facets jsonb,
    p_messages jsonb
) RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    v_new_context_version bigint;
BEGIN
    IF jsonb_typeof(p_patch) <> 'object' OR p_patch = '{}'::jsonb THEN
        RAISE EXCEPTION 'experience patch must be a non-empty object'
            USING ERRCODE = '22023';
    END IF;
    IF jsonb_typeof(p_changed_facets) <> 'array'
       OR jsonb_array_length(p_changed_facets) = 0 THEN
        RAISE EXCEPTION 'changed facets must be a non-empty array'
            USING ERRCODE = '22023';
    END IF;
    IF EXISTS (
        SELECT 1
          FROM jsonb_array_elements_text(p_changed_facets) AS changed(state_facet)
          LEFT JOIN orchestration.projection_dependency dependency USING (state_facet)
         WHERE dependency.state_facet IS NULL
            OR p_patch #> string_to_array(changed.state_facet, '.') IS NULL
    ) THEN
        RAISE EXCEPTION 'unknown experience-state facet'
            USING ERRCODE = '22023';
    END IF;

    UPDATE orchestration.experience_session
       SET state_schema_version = p_state_schema_version,
           state = orchestration.jsonb_deep_merge(state, p_patch),
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
    SELECT p_session_id, v_new_context_version, dependency.projection_key,
           string_agg(DISTINCT dependency.reason, ', ' ORDER BY dependency.reason)
      FROM jsonb_array_elements_text(p_changed_facets) AS changed(state_facet)
      JOIN orchestration.projection_dependency dependency USING (state_facet)
     GROUP BY dependency.projection_key;

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

INSERT INTO orchestration.schema_migration(version) VALUES (4);
COMMIT;
