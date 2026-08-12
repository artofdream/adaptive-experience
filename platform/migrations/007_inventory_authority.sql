BEGIN;

CREATE SCHEMA IF NOT EXISTS inventory;

CREATE TABLE inventory.product_availability (
    product_id text PRIMARY KEY CHECK (product_id <> ''),
    available_quantity integer NOT NULL CHECK (available_quantity >= 0),
    source_version bigint NOT NULL CHECK (source_version >= 0),
    observed_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX product_availability_observed_idx
    ON inventory.product_availability (observed_at);

INSERT INTO orchestration.schema_migration(version) VALUES (7);
COMMIT;
