"""
User database connection endpoints.

POST   /api/connections           add a connection (test + introspect + embed)
GET    /api/connections           list saved connections
DELETE /api/connections/{id}      remove connection and its embeddings
POST   /api/connections/{id}/refresh  re-introspect schema
"""
from __future__ import annotations

import re
import time
import uuid
from collections import defaultdict
from typing import Any

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Depends, HTTPException
from google import genai
from google.genai import types as gtypes
from pydantic import BaseModel

from api.auth import TokenData, get_current_user
from api.config import settings

EMBEDDING_MODEL = "gemini-embedding-001"
MAX_TABLES = 60
MAX_COLS_PER_TABLE = 40

router = APIRouter(prefix="/api/connections", tags=["connections"])


class ConnectionCreate(BaseModel):
    name: str
    connection_url: str


class ConnectionMeta(BaseModel):
    id: int
    name: str
    table_count: int
    schema_version: str
    created_at: str


def _validate_url(url: str) -> None:
    if not re.match(r"^(postgresql|postgres)://", url):
        raise HTTPException(400, "Only PostgreSQL connection strings are supported (postgresql://...)")


def _test_connection(url: str) -> None:
    try:
        conn = psycopg2.connect(url, connect_timeout=8)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
    except Exception as exc:
        raise HTTPException(400, f"Could not connect: {exc}") from exc


def _introspect(url: str) -> dict[str, list[dict[str, str]]]:
    """Return {table_name: [{column_name, data_type}]} for user-visible tables."""
    conn = psycopg2.connect(url, connect_timeout=8)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT c.table_name, c.column_name, c.data_type
                FROM information_schema.columns c
                JOIN information_schema.tables t
                    ON c.table_name = t.table_name
                    AND c.table_schema = t.table_schema
                WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema')
                  AND t.table_type = 'BASE TABLE'
                ORDER BY c.table_name, c.ordinal_position
            """)
            rows = cur.fetchall()
    finally:
        conn.close()

    tables: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        if len(tables) >= MAX_TABLES and r["table_name"] not in tables:
            continue
        if len(tables[r["table_name"]]) < MAX_COLS_PER_TABLE:
            tables[r["table_name"]].append({
                "column_name": r["column_name"],
                "data_type": r["data_type"],
            })
    return dict(tables)


def _embed_texts(texts: list[str]) -> list[list[float]]:
    client = genai.Client(api_key=settings.gemini_api_key)
    results: list[list[float]] = []
    for text in texts:
        resp = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=gtypes.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768,
            ),
        )
        results.append(list(resp.embeddings[0].values))
        time.sleep(0.05)
    return results


def _store_schema_embeddings(
    conn: "psycopg2.extensions.connection",
    schema_version: str,
    db_name: str,
    tables: dict[str, list[dict[str, str]]],
) -> None:
    entries: list[dict[str, Any]] = []

    for table_name, cols in tables.items():
        col_summary = ", ".join(f"{c['column_name']} ({c['data_type']})" for c in cols)
        entries.append({
            "entry_type": "table",
            "table_name": table_name,
            "column_name": None,
            "data_type": None,
            "description": f"Table {table_name} from {db_name}",
            "sample_values": None,
            "content": f"Table: {table_name} (database: {db_name}). Columns: {col_summary}.",
        })
        for col in cols:
            entries.append({
                "entry_type": "column",
                "table_name": table_name,
                "column_name": col["column_name"],
                "data_type": col["data_type"],
                "description": f"Column {col['column_name']} of type {col['data_type']} in {table_name}",
                "sample_values": None,
                "content": (
                    f"Column '{col['column_name']}' in table {table_name} ({db_name}). "
                    f"Type: {col['data_type']}."
                ),
            })

    texts = [e["content"] for e in entries]
    embeddings = _embed_texts(texts)

    with conn.cursor() as cur:
        cur.execute("DELETE FROM schema_embeddings WHERE schema_version = %s", (schema_version,))
        for entry, emb in zip(entries, embeddings):
            emb_str = "[" + ",".join(str(v) for v in emb) + "]"
            cur.execute("""
                INSERT INTO schema_embeddings
                    (schema_version, entry_type, database_name, table_name,
                     column_name, data_type, description, sample_values,
                     fk_references, content, embedding)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::vector)
            """, (
                schema_version, entry["entry_type"], db_name,
                entry["table_name"], entry["column_name"], entry["data_type"],
                entry["description"], entry["sample_values"], None,
                entry["content"], emb_str,
            ))
    conn.commit()


@router.post("", response_model=ConnectionMeta)
def add_connection(
    body: ConnectionCreate,
    current_user: TokenData = Depends(get_current_user),
) -> ConnectionMeta:
    _validate_url(body.connection_url)
    _test_connection(body.connection_url)

    tables = _introspect(body.connection_url)
    if not tables:
        raise HTTPException(400, "No user tables found in this database")

    schema_version = f"conn_{uuid.uuid4().hex[:12]}"

    admin_conn = psycopg2.connect(settings.database_url)
    try:
        _store_schema_embeddings(admin_conn, schema_version, body.name, tables)
        with admin_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_connections
                    (user_id, name, connection_url, schema_version, table_count)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (current_user.user_id, body.name, body.connection_url, schema_version, len(tables)))
            row = cur.fetchone()
        admin_conn.commit()
    finally:
        admin_conn.close()

    return ConnectionMeta(
        id=row[0],
        name=body.name,
        table_count=len(tables),
        schema_version=schema_version,
        created_at=str(row[1]),
    )


@router.get("", response_model=list[ConnectionMeta])
def list_connections() -> list[ConnectionMeta]:
    conn = psycopg2.connect(settings.database_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, table_count, schema_version, created_at
                FROM user_connections
                ORDER BY created_at DESC
                LIMIT 50
            """)
            rows = cur.fetchall()
    finally:
        conn.close()
    return [ConnectionMeta(
        id=r["id"], name=r["name"], table_count=r["table_count"],
        schema_version=r["schema_version"], created_at=str(r["created_at"]),
    ) for r in rows]


@router.delete("/{conn_id}", status_code=204)
def delete_connection(
    conn_id: int,
    current_user: TokenData = Depends(get_current_user),
) -> None:
    admin_conn = psycopg2.connect(settings.database_url)
    try:
        with admin_conn.cursor() as cur:
            cur.execute(
                "SELECT schema_version FROM user_connections WHERE id = %s", (conn_id,)
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "Connection not found")
            schema_version = row[0]
            cur.execute("DELETE FROM schema_embeddings WHERE schema_version = %s", (schema_version,))
            cur.execute("DELETE FROM user_connections WHERE id = %s", (conn_id,))
        admin_conn.commit()
    finally:
        admin_conn.close()


@router.post("/{conn_id}/refresh", response_model=ConnectionMeta)
def refresh_connection(
    conn_id: int,
    current_user: TokenData = Depends(get_current_user),
) -> ConnectionMeta:
    admin_conn = psycopg2.connect(settings.database_url)
    try:
        with admin_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT name, connection_url, schema_version FROM user_connections WHERE id = %s",
                (conn_id,),
            )
            row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Connection not found")

        tables = _introspect(row["connection_url"])
        _store_schema_embeddings(admin_conn, row["schema_version"], row["name"], tables)

        with admin_conn.cursor() as cur:
            cur.execute(
                "UPDATE user_connections SET table_count = %s WHERE id = %s RETURNING created_at",
                (len(tables), conn_id),
            )
            updated = cur.fetchone()
        admin_conn.commit()
    finally:
        admin_conn.close()

    return ConnectionMeta(
        id=conn_id, name=row["name"], table_count=len(tables),
        schema_version=row["schema_version"], created_at=str(updated[0]),
    )


def get_connection_url(conn_id: int) -> tuple[str, str]:
    """Return (connection_url, schema_version) for a saved connection."""
    conn = psycopg2.connect(settings.database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT connection_url, schema_version FROM user_connections WHERE id = %s",
                (conn_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        raise HTTPException(404, "Connection not found")
    return row[0], row[1]
