BEGIN;

INSERT INTO orchestration.projection_dependency(state_facet, projection_key, reason)
VALUES ('shared_understanding.flower_preference', 'recommendations', 'intent_changed'),
       ('thought_completion.suggestions', 'conversation', 'suggestions_updated');

INSERT INTO orchestration.schema_migration(version) VALUES (6);
COMMIT;
