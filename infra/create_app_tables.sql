-- Application tables for QueryPilot
-- Run this in the Supabase SQL editor after create_pgvector_tables.sql

CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR        NOT NULL,
    is_active       BOOLEAN        DEFAULT TRUE,
    created_at      TIMESTAMPTZ    DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS users_email_idx ON users (email);

CREATE TABLE IF NOT EXISTS query_history (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER,
    question        TEXT          NOT NULL,
    schema_version  VARCHAR(20)   NOT NULL DEFAULT 'v1',
    final_sql       TEXT,
    success         BOOLEAN       NOT NULL DEFAULT FALSE,
    iterations      INTEGER       NOT NULL DEFAULT 1,
    latency_ms      INTEGER,
    error_trace     TEXT,
    semantic_score  INTEGER,
    semantic_note   TEXT,
    row_count       INTEGER,
    truncated       BOOLEAN       DEFAULT FALSE,
    created_at      TIMESTAMP     DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS feedback (
    id              SERIAL PRIMARY KEY,
    query_id        INTEGER REFERENCES query_history(id) ON DELETE CASCADE,
    user_id         INTEGER,
    rating          INTEGER       CHECK (rating BETWEEN 1 AND 5),
    comment         TEXT,
    created_at      TIMESTAMP     DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS query_history_created_idx ON query_history (created_at DESC);
CREATE INDEX IF NOT EXISTS query_history_user_idx    ON query_history (user_id);
CREATE INDEX IF NOT EXISTS feedback_query_idx        ON feedback (query_id);

-- Grant sandbox role read access to query history for debugging
GRANT SELECT ON query_history TO querypilot_readonly;
