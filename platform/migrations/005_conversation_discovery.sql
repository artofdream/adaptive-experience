BEGIN;

INSERT INTO orchestration.projection_dependency(state_facet, projection_key, reason)
VALUES ('conversation.messages', 'conversation', 'customer_message_submitted');

INSERT INTO orchestration.schema_migration(version) VALUES (5);
COMMIT;
