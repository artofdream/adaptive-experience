-- Migration 020: Stem-by-Stem Inventory Catalog (GAP-V01)
-- Supports interactive bouquet stem composition, unit pricing, and stock tracking

BEGIN;

CREATE TABLE IF NOT EXISTS stem_inventory (
    stem_id VARCHAR(64) PRIMARY KEY,
    stem_name VARCHAR(128) NOT NULL,
    flower_type VARCHAR(64) NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    available_stock INTEGER NOT NULL DEFAULT 500,
    pet_safe BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO stem_inventory (stem_id, stem_name, flower_type, unit_price_cents, available_stock, pet_safe) VALUES
('stem-rose-red', 'Classic Red Rose', 'roses', 450, 1000, true),
('stem-lily-white', 'Oriental White Lily', 'lilies', 650, 450, false), -- toxic to cats
('stem-carnation-pink', 'Pink Carnation', 'carnations', 300, 800, true),
('stem-orchid-phalaenopsis', 'Phalaenopsis Orchid Stem', 'orchids', 850, 300, true),
('stem-eucalyptus-silver', 'Silver Dollar Eucalyptus', 'foliage', 250, 1200, true)
ON CONFLICT (stem_id) DO NOTHING;

INSERT INTO orchestration.schema_migration(version) VALUES (20);
COMMIT;
