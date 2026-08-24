-- Migration 021: Vector-Based Semantic Intent Cache (GAP-V03)
-- Caches pre-computed LLM intent interpretations for zero-latency response lookups

CREATE TABLE IF NOT EXISTS semantic_intent_cache (
    cache_id VARCHAR(64) PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_hash VARCHAR(64) NOT NULL UNIQUE,
    structured_intent_json JSONB NOT NULL,
    hit_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_semantic_cache_hash ON semantic_intent_cache(query_hash);
