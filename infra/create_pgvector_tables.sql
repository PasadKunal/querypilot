-- Run this in your Supabase SQL editor AFTER running postgres_roles.sql
-- Requires the pgvector extension to be enabled:
--   CREATE EXTENSION IF NOT EXISTS vector;

-- Main table that stores one row per embedded schema entry.
-- entry_type can be: 'table', 'column', or 'foreign_key'
-- embedding dimension 1536 matches text-embedding-3-small output.

CREATE TABLE IF NOT EXISTS schema_embeddings (
    id              SERIAL PRIMARY KEY,
    schema_version  VARCHAR(20)   NOT NULL DEFAULT 'v1',
    entry_type      VARCHAR(20)   NOT NULL,
    database_name   VARCHAR(100)  NOT NULL,
    table_name      VARCHAR(100)  NOT NULL,
    column_name     VARCHAR(100),
    data_type       VARCHAR(50),
    description     TEXT,
    sample_values   JSONB,
    fk_references   VARCHAR(300),
    content         TEXT          NOT NULL,
    embedding       vector(1536),
    created_at      TIMESTAMP     DEFAULT NOW()
);

-- IVFFlat cosine index for fast approximate nearest-neighbor search.
-- lists=100 is a good default for tables up to ~1 million rows.
CREATE INDEX IF NOT EXISTS schema_embeddings_embedding_idx
    ON schema_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Index on schema_version so incremental re-embedding queries are fast.
CREATE INDEX IF NOT EXISTS schema_embeddings_version_idx
    ON schema_embeddings (schema_version, database_name, table_name);

-- Grant the read-only sandbox role SELECT access on this table.
GRANT SELECT ON schema_embeddings TO querypilot_readonly;
