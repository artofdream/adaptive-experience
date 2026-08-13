BEGIN;

-- Drop the superseded state-mutation function. apply_experience_patch (migration
-- 004, deep-merge + dependency-driven invalidation) is the sole state-mutation
-- path; apply_experience_mutation has had no application caller since then.
DROP FUNCTION IF EXISTS orchestration.apply_experience_mutation(
    uuid, bigint, integer, jsonb, jsonb, jsonb);

INSERT INTO orchestration.schema_migration(version) VALUES (11);
COMMIT;
