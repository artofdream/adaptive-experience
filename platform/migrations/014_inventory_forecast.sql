BEGIN;

CREATE TABLE inventory.availability_observation (
    product_id text NOT NULL CHECK (product_id <> ''),
    available_quantity integer NOT NULL CHECK (available_quantity >= 0),
    source_version bigint NOT NULL CHECK (source_version >= 0),
    observed_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (product_id, source_version)
);

CREATE INDEX availability_observation_observed_idx
    ON inventory.availability_observation (product_id, observed_at);

INSERT INTO inventory.availability_observation
    (product_id, available_quantity, source_version, observed_at, recorded_at)
SELECT product_id, available_quantity, source_version, observed_at, updated_at
FROM inventory.product_availability
ON CONFLICT (product_id, source_version) DO NOTHING;

INSERT INTO orchestration.schema_migration(version) VALUES (14);
COMMIT;
