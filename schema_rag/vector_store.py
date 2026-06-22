"""
Vector similarity search against the schema_embeddings pgvector table.

At query time: embed the user's question -> cosine similarity search -> return
the top-k most relevant schema entries (tables, columns, and FK relationships).
"""

from __future__ import annotations

from typing import Any

import psycopg2
import psycopg2.extras
from openai import OpenAI

from api.config import settings


EMBEDDING_MODEL = "text-embedding-3-small"


class VectorStore:
    def __init__(self, db_url: str | None = None, openai_client: OpenAI | None = None) -> None:
        self.db_url = db_url or settings.database_url
        self.client = openai_client or OpenAI(api_key=settings.openai_api_key)

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=EMBEDDING_MODEL, input=[text])
        return response.data[0].embedding

    def search(
        self,
        query: str,
        top_k: int = 15,
        schema_version: str = "v1",
        entry_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Embed the query and return the top-k most similar schema entries.
        Optionally filter by entry_type ('table', 'column', 'foreign_key').
        """
        query_embedding = self.embed_query(query)
        embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

        type_filter = ""
        params: list[Any] = [schema_version, embedding_str, top_k]
        if entry_types:
            placeholders = ",".join(["%s"] * len(entry_types))
            type_filter = f"AND entry_type IN ({placeholders})"
            params = [schema_version] + entry_types + [embedding_str, top_k]

        sql = f"""
            SELECT
                id,
                entry_type,
                database_name,
                table_name,
                column_name,
                data_type,
                description,
                sample_values,
                fk_references,
                content,
                1 - (embedding <=> %s::vector) AS similarity
            FROM schema_embeddings
            WHERE schema_version = %s
            {type_filter}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        # Reorder params: version, (optional types), embedding for similarity, embedding for ORDER BY, top_k
        if entry_types:
            sql_params = [schema_version] + entry_types + [embedding_str, embedding_str, top_k]
        else:
            sql_params = [schema_version, embedding_str, embedding_str, top_k]

        conn = psycopg2.connect(self.db_url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, sql_params)
                rows = cur.fetchall()
        finally:
            conn.close()

        return [dict(row) for row in rows]

    def get_relevant_tables(self, query: str, top_k: int = 5, schema_version: str = "v1") -> list[str]:
        """Return deduplicated table names from the top-k search results."""
        results = self.search(query, top_k=top_k * 3, schema_version=schema_version)
        seen: set[str] = set()
        tables: list[str] = []
        for row in results:
            if row["table_name"] not in seen:
                seen.add(row["table_name"])
                tables.append(row["table_name"])
            if len(tables) >= top_k:
                break
        return tables
