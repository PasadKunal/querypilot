"""
Schema embedding pipeline.

Reads SCHEMA_METADATA, converts each table/column/FK entry into a text string,
calls Gemini text-embedding-004 (free tier), and upserts the result into the
schema_embeddings pgvector table in Supabase.

Run as a one-time setup script or after schema changes:
    python -m schema_rag.embedder
"""

from __future__ import annotations

import json
import time
from typing import Any

import psycopg2
import psycopg2.extras
from google import genai
from google.genai import types

from api.config import settings
from datasets.schema_metadata import SCHEMA_METADATA


EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768
BATCH_SIZE = 50
RATE_LIMIT_SLEEP = 0.5


class SchemaEmbedder:
    def __init__(self, gemini_api_key: str | None = None, db_url: str | None = None) -> None:
        self.db_url = db_url or settings.database_url
        self.client = genai.Client(api_key=gemini_api_key or settings.gemini_api_key)

    def run(self, schema_version: str = "v1") -> int:
        """Embed all entries in SCHEMA_METADATA and upsert them into pgvector. Returns total rows written."""
        entries = self._build_all_entries(schema_version)
        print(f"Built {len(entries)} entries to embed.")

        texts = [e["content"] for e in entries]
        embeddings = self._embed_in_batches(texts)

        for entry, embedding in zip(entries, embeddings):
            entry["embedding"] = embedding

        self._upsert_entries(entries, schema_version)
        print(f"Upserted {len(entries)} embedding records (schema_version={schema_version}).")
        return len(entries)

    def _build_all_entries(self, schema_version: str) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []

        for db_name, db_info in SCHEMA_METADATA.items():
            tables = db_info.get("tables", {})
            fks = db_info.get("foreign_keys", [])

            for table_name, table_info in tables.items():
                col_names = list(table_info.get("columns", {}).keys())
                content = (
                    f"Table: {table_name} (database: {db_name}). "
                    f"{table_info['description']} "
                    f"Columns: {', '.join(col_names)}."
                )
                entries.append({
                    "schema_version": schema_version,
                    "entry_type": "table",
                    "database_name": db_name,
                    "table_name": table_name,
                    "column_name": None,
                    "data_type": None,
                    "description": table_info["description"],
                    "sample_values": None,
                    "fk_references": None,
                    "content": content,
                })

                for col_name, col_info in table_info.get("columns", {}).items():
                    sample_vals = col_info.get("sample_values", [])
                    sample_str = ", ".join(str(v) for v in sample_vals[:5])
                    content = (
                        f"Column: {table_name}.{col_name} (type: {col_info['type']}). "
                        f"{col_info['description']} "
                        f"Sample values: {sample_str}."
                    )
                    entries.append({
                        "schema_version": schema_version,
                        "entry_type": "column",
                        "database_name": db_name,
                        "table_name": table_name,
                        "column_name": col_name,
                        "data_type": col_info["type"],
                        "description": col_info["description"],
                        "sample_values": json.dumps(sample_vals),
                        "fk_references": None,
                        "content": content,
                    })

            for fk in fks:
                ref = f"{fk['from_table']}.{fk['from_column']} -> {fk['to_table']}.{fk['to_column']}"
                content = (
                    f"Foreign key relationship: {ref}. "
                    f"Use JOIN {fk['to_table']} ON {fk['from_table']}.{fk['from_column']} "
                    f"= {fk['to_table']}.{fk['to_column']} "
                    f"when connecting {fk['from_table']} to {fk['to_table']}."
                )
                entries.append({
                    "schema_version": schema_version,
                    "entry_type": "foreign_key",
                    "database_name": db_name,
                    "table_name": fk["from_table"],
                    "column_name": fk["from_column"],
                    "data_type": None,
                    "description": f"FK from {fk['from_table']}.{fk['from_column']} to {fk['to_table']}.{fk['to_column']}",
                    "sample_values": None,
                    "fk_references": ref,
                    "content": content,
                })

        return entries

    def _embed_in_batches(self, texts: list[str]) -> list[list[float]]:
        all_embeddings: list[list[float]] = []
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i: i + BATCH_SIZE]
            response = self.client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT", output_dimensionality=768),
            )
            batch_embeddings = [list(e.values) for e in response.embeddings]
            all_embeddings.extend(batch_embeddings)
            print(f"  Embedded batch {i // BATCH_SIZE + 1}/{(len(texts) - 1) // BATCH_SIZE + 1}")
            time.sleep(RATE_LIMIT_SLEEP)
        return all_embeddings

    def _upsert_entries(self, entries: list[dict[str, Any]], schema_version: str) -> None:
        conn = psycopg2.connect(self.db_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM schema_embeddings WHERE schema_version = %s",
                    (schema_version,),
                )
                psycopg2.extras.execute_values(
                    cur,
                    """
                    INSERT INTO schema_embeddings
                        (schema_version, entry_type, database_name, table_name,
                         column_name, data_type, description, sample_values,
                         fk_references, content, embedding)
                    VALUES %s
                    """,
                    [
                        (
                            e["schema_version"],
                            e["entry_type"],
                            e["database_name"],
                            e["table_name"],
                            e["column_name"],
                            e["data_type"],
                            e["description"],
                            e["sample_values"],
                            e["fk_references"],
                            e["content"],
                            e["embedding"],
                        )
                        for e in entries
                    ],
                )
            conn.commit()
        finally:
            conn.close()


if __name__ == "__main__":
    embedder = SchemaEmbedder()
    total = embedder.run(schema_version="v1")
    print(f"Done. {total} records written to schema_embeddings.")
