"""
CSV upload endpoints.

POST   /api/tables/upload        upload a CSV, create table, embed schema
GET    /api/tables               list all uploaded tables
DELETE /api/tables/{table_name}  drop table + embeddings
"""
from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from google import genai
from google.genai import types as gtypes
from pydantic import BaseModel

from api.auth import TokenData, get_current_user
from api.config import settings
from datasets.csv_processor import parse_csv

EMBEDDING_MODEL = "gemini-embedding-001"
MAX_ROWS = 50_000
MAX_FILE_BYTES = 20 * 1024 * 1024  # 20 MB

router = APIRouter(prefix="/api/tables", tags=["tables"])


class ColumnInfo(BaseModel):
    name: str
    pg_type: str


class UserTableMeta(BaseModel):
    table_name: str
    display_name: str
    row_count: int
    column_count: int
    columns: list[ColumnInfo]
    created_at: str


def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]", "_", name.lower())
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:20] or "table"


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


def _create_and_populate(
    conn: "psycopg2.extensions.connection",
    table_name: str,
    headers: list[str],
    col_types: dict[str, str],
    rows: list[dict[str, Any]],
) -> None:
    col_defs = ", ".join(f'"{h}" {col_types[h]}' for h in headers)
    with conn.cursor() as cur:
        cur.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({col_defs})')
        if rows:
            col_list = ", ".join(f'"{h}"' for h in headers)
            placeholders = ", ".join(["%s"] * len(headers))
            insert_sql = f'INSERT INTO "{table_name}" ({col_list}) VALUES ({placeholders})'
            batch = [[r.get(h) for h in headers] for r in rows]
            psycopg2.extras.execute_batch(cur, insert_sql, batch, page_size=500)
    conn.commit()


def _grant_sandbox(conn: "psycopg2.extensions.connection", table_name: str) -> None:
    with conn.cursor() as cur:
        try:
            cur.execute(f'GRANT SELECT ON "{table_name}" TO querypilot_sandbox')
            conn.commit()
        except Exception:
            conn.rollback()


def _store_embeddings(
    conn: "psycopg2.extensions.connection",
    table_name: str,
    display_name: str,
    headers: list[str],
    col_types: dict[str, str],
    rows: list[dict[str, Any]],
) -> None:
    col_summary = ", ".join(f"{h} ({col_types[h]})" for h in headers)
    table_content = (
        f"Table: {table_name} (user uploaded: {display_name}). "
        f"Columns: {col_summary}."
    )

    entries: list[dict[str, Any]] = [{
        "entry_type": "table",
        "database_name": "user_uploads",
        "table_name": table_name,
        "column_name": None,
        "data_type": None,
        "description": f"User-uploaded table from '{display_name}'",
        "sample_values": None,
        "fk_references": None,
        "content": table_content,
    }]

    sample_rows = rows[:5]
    for col in headers:
        samples = [str(r[col]) for r in sample_rows if r.get(col) is not None]
        sample_str = json.dumps(samples[:3]) if samples else None
        col_content = (
            f"Column '{col}' in table {table_name} ({display_name}). "
            f"Type: {col_types[col]}."
            + (f" Sample values: {', '.join(samples[:3])}." if samples else "")
        )
        entries.append({
            "entry_type": "column",
            "database_name": "user_uploads",
            "table_name": table_name,
            "column_name": col,
            "data_type": col_types[col],
            "description": f"Column {col} of type {col_types[col]}",
            "sample_values": sample_str,
            "fk_references": None,
            "content": col_content,
        })

    texts = [e["content"] for e in entries]
    embeddings = _embed_texts(texts)

    with conn.cursor() as cur:
        for entry, emb in zip(entries, embeddings):
            emb_str = "[" + ",".join(str(v) for v in emb) + "]"
            cur.execute("""
                INSERT INTO schema_embeddings
                    (schema_version, entry_type, database_name, table_name,
                     column_name, data_type, description, sample_values,
                     fk_references, content, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
            """, (
                "v1",
                entry["entry_type"],
                entry["database_name"],
                entry["table_name"],
                entry["column_name"],
                entry["data_type"],
                entry["description"],
                entry["sample_values"],
                entry["fk_references"],
                entry["content"],
                emb_str,
            ))
    conn.commit()


def _save_meta(
    conn: "psycopg2.extensions.connection",
    table_name: str,
    display_name: str,
    user_id: int | None,
    row_count: int,
    headers: list[str],
    col_types: dict[str, str],
) -> None:
    columns_json = json.dumps([{"name": h, "pg_type": col_types[h]} for h in headers])
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO user_tables
                (table_name, display_name, user_id, row_count, column_count, columns_json)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (table_name, display_name, user_id, row_count, len(headers), columns_json))
    conn.commit()


@router.post("/upload", response_model=UserTableMeta)
async def upload_csv(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
) -> UserTableMeta:
    filename = file.filename or "data.csv"
    if not any(filename.lower().endswith(ext) for ext in (".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only .csv, .xlsx, and .xls files are supported")

    raw = await file.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 20 MB)")

    try:
        headers, rows, col_types = parse_csv(raw, filename)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {exc}") from exc

    if len(rows) > MAX_ROWS:
        rows = rows[:MAX_ROWS]

    stem = Path(file.filename or "data").stem
    table_name = f"ut_{uuid.uuid4().hex[:8]}_{_slug(stem)}"
    display_name = stem[:120]

    conn = psycopg2.connect(settings.database_url)
    try:
        _create_and_populate(conn, table_name, headers, col_types, rows)
        _grant_sandbox(conn, table_name)
        _store_embeddings(conn, table_name, display_name, headers, col_types, rows)
        _save_meta(conn, table_name, display_name, current_user.user_id, len(rows), headers, col_types)
    except Exception as exc:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}") from exc
    finally:
        conn.close()

    return UserTableMeta(
        table_name=table_name,
        display_name=display_name,
        row_count=len(rows),
        column_count=len(headers),
        columns=[ColumnInfo(name=h, pg_type=col_types[h]) for h in headers],
        created_at="",
    )


@router.get("", response_model=list[UserTableMeta])
def list_tables() -> list[UserTableMeta]:
    conn = psycopg2.connect(settings.database_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT table_name, display_name, row_count, column_count,
                       columns_json, created_at
                FROM user_tables
                ORDER BY created_at DESC
                LIMIT 100
            """)
            rows = cur.fetchall()
    finally:
        conn.close()

    result: list[UserTableMeta] = []
    for r in rows:
        raw = r["columns_json"] or []
        cols: list[dict[str, str]] = raw if isinstance(raw, list) else json.loads(raw)
        result.append(UserTableMeta(
            table_name=r["table_name"],
            display_name=r["display_name"],
            row_count=r["row_count"],
            column_count=r["column_count"],
            columns=[ColumnInfo(name=c["name"], pg_type=c["pg_type"]) for c in cols],
            created_at=str(r["created_at"]),
        ))
    return result


@router.delete("/{table_name}", status_code=204)
def delete_table(
    table_name: str,
    current_user: TokenData = Depends(get_current_user),
) -> None:
    if not re.fullmatch(r"ut_[0-9a-f]{8}_[a-z0-9_]+", table_name):
        raise HTTPException(status_code=400, detail="Invalid table name")

    conn = psycopg2.connect(settings.database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(f'DROP TABLE IF EXISTS "{table_name}"')
            cur.execute("DELETE FROM schema_embeddings WHERE table_name = %s", (table_name,))
            cur.execute("DELETE FROM user_tables WHERE table_name = %s", (table_name,))
        conn.commit()
    finally:
        conn.close()
