BEGIN;

-- Retrieval-owned schema (ADR-014). Experience-state tables do not depend on
-- pgvector; embeddings live beside relational filters, not in orchestration.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE SCHEMA IF NOT EXISTS retrieval;

-- Approved knowledge chunks for hybrid retrieval (ADR-015). Vector dimension
-- is a scaffold default; production model choice remains an implementation
-- detail under ADR-014. Body is the approved text; terms hold extra lexical
-- anchors (FAQ keywords) for the FTS path.
CREATE TABLE retrieval.knowledge_chunk (
    chunk_id text PRIMARY KEY CHECK (char_length(btrim(chunk_id)) BETWEEN 1 AND 100),
    source_reference text NOT NULL CHECK (char_length(btrim(source_reference)) BETWEEN 1 AND 100),
    body text NOT NULL CHECK (char_length(btrim(body)) BETWEEN 1 AND 4000),
    terms text NOT NULL DEFAULT '' CHECK (char_length(terms) <= 500),
    embedding vector(32) NOT NULL,
    search_tsv tsvector GENERATED ALWAYS AS (
        to_tsvector('english', body || ' ' || terms)
    ) STORED,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX knowledge_chunk_embedding_hnsw
    ON retrieval.knowledge_chunk
    USING hnsw (embedding vector_cosine_ops);

CREATE INDEX knowledge_chunk_fts_idx
    ON retrieval.knowledge_chunk
    USING gin (search_tsv);

CREATE INDEX knowledge_chunk_source_idx
    ON retrieval.knowledge_chunk (source_reference);

INSERT INTO orchestration.schema_migration(version) VALUES (13);
COMMIT;
