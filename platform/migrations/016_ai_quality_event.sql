BEGIN;

CREATE TABLE orchestration.ai_quality_event (
    event_id uuid PRIMARY KEY,
    path text NOT NULL CHECK (path IN ('intent', 'faq')),
    outcome text NOT NULL CHECK (outcome IN ('ok', 'fallback', 'unmatched', 'error')),
    error_code text CHECK (
        error_code IS NULL OR error_code IN (
            'provider_unavailable',
            'invalid_output',
            'unsupported_facets',
            'unapproved_answer'
        )
    ),
    quality_flags text[] NOT NULL DEFAULT '{}',
    assistant_mode text CHECK (
        assistant_mode IS NULL OR assistant_mode IN ('primary', 'fallback', 'reference')
    ),
    matched boolean,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK (quality_flags <@ ARRAY[
        'approved_source', 'supported_facets', 'no_fabrication', 'degraded'
    ]::text[]),
    CHECK (path <> 'intent' OR assistant_mode IS NOT NULL),
    CHECK (path <> 'faq' OR matched IS NOT NULL),
    CHECK (outcome <> 'error' OR error_code IS NOT NULL),
    CHECK (error_code IS NULL OR outcome IN ('error', 'fallback'))
);

CREATE INDEX ai_quality_event_recorded_idx
    ON orchestration.ai_quality_event (path, recorded_at DESC);

INSERT INTO orchestration.schema_migration(version) VALUES (16);
COMMIT;
