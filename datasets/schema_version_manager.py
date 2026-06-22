"""
Schema version manager.

Tracks which schema version is currently active and handles incremental
re-embedding when tables or columns change. Only modified entries are
re-embedded, not the full schema.
"""

from __future__ import annotations

import psycopg2
import psycopg2.extras

from api.config import settings


class SchemaVersionManager:
    def __init__(self, db_url: str | None = None) -> None:
        self.db_url = db_url or settings.database_url

    def get_current_version(self) -> str | None:
        """Return the most recently written schema version, or None if the table is empty."""
        conn = psycopg2.connect(self.db_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT schema_version FROM schema_embeddings ORDER BY created_at DESC LIMIT 1"
                )
                row = cur.fetchone()
                return row[0] if row else None
        finally:
            conn.close()

    def list_versions(self) -> list[str]:
        """Return all distinct schema versions stored in the embeddings table."""
        conn = psycopg2.connect(self.db_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT DISTINCT schema_version FROM schema_embeddings ORDER BY schema_version"
                )
                return [row[0] for row in cur.fetchall()]
        finally:
            conn.close()

    def delete_version(self, schema_version: str) -> int:
        """Delete all embedding records for the given version. Returns rows deleted."""
        conn = psycopg2.connect(self.db_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM schema_embeddings WHERE schema_version = %s",
                    (schema_version,),
                )
                deleted = cur.rowcount
            conn.commit()
            return deleted
        finally:
            conn.close()

    def tag_queries_as_stale(self, schema_version: str, db_conn_url: str | None = None) -> int:
        """
        Mark query_history rows generated against an old schema version as stale.
        Returns number of rows updated.
        """
        url = db_conn_url or self.db_url
        conn = psycopg2.connect(url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE query_history
                    SET schema_version = %s
                    WHERE schema_version != %s
                    """,
                    (f"{schema_version}_stale", schema_version),
                )
                updated = cur.rowcount
            conn.commit()
            return updated
        finally:
            conn.close()
