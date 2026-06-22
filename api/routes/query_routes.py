"""
POST /api/query  - natural language to SQL endpoint.

Full pipeline:
  1. Embed the question and retrieve relevant schema chunks from pgvector
  2. Assemble schema context (FK join paths + disambiguation)
  3. Run the 3-iteration self-correction loop (generate -> validate -> execute)
  4. Semantic check on the result
  5. Persist to query_history
  6. Return the result to the client
"""

from __future__ import annotations

import psycopg2
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from api.config import settings
from api.routes.connection_routes import get_connection_url
from schema_rag.context_assembler import ContextAssembler
from sql_agent import semantic_checker
from sql_agent.corrector import SelfCorrector

router = APIRouter(prefix="/api", tags=["query"])

_assembler: ContextAssembler | None = None
_corrector: SelfCorrector | None = None


def _get_assembler() -> ContextAssembler:
    global _assembler
    if _assembler is None:
        _assembler = ContextAssembler()
    return _assembler


def _get_corrector() -> SelfCorrector:
    global _corrector
    if _corrector is None:
        _corrector = SelfCorrector()
    return _corrector


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)
    schema_version: str = Field(default="v1")
    run_semantic_check: bool = Field(default=True)
    connection_id: int | None = Field(default=None)


class QueryResponse(BaseModel):
    success: bool
    query_id: int | None = None
    question: str
    sql: str
    rows: list[dict] = []
    row_count: int = 0
    columns: list[str] = []
    truncated: bool = False
    reasoning: str = ""
    confidence: float = 0.0
    iterations: int = 0
    latency_ms: int = 0
    semantic_score: int | None = None
    semantic_note: str | None = None
    error: str | None = None


def _save_to_history(result, semantic, question: str, schema_version: str) -> int | None:
    try:
        conn = psycopg2.connect(settings.database_url)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO query_history
                    (question, schema_version, final_sql, success, iterations,
                     latency_ms, error_trace, semantic_score, semantic_note,
                     row_count, truncated)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
                """,
                (
                    question,
                    schema_version,
                    result.sql,
                    result.success,
                    result.iterations,
                    result.latency_ms,
                    result.error_trace or None,
                    semantic.score if semantic else None,
                    semantic.explanation if semantic else None,
                    result.row_count,
                    result.truncated,
                ),
            )
            row = cur.fetchone()
        conn.commit()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None  # history is best-effort; never fail the user response


@router.post("/query", response_model=QueryResponse)
def run_query(payload: QueryRequest) -> QueryResponse:
    assembler = _get_assembler()
    corrector = _get_corrector()

    db_url: str | None = None
    schema_version = payload.schema_version
    if payload.connection_id is not None:
        db_url, schema_version = get_connection_url(payload.connection_id)

    schema_context = assembler.assemble(
        query=payload.question,
        schema_version=schema_version,
    )

    result = corrector.run(
        question=payload.question,
        schema_context=schema_context,
        max_iterations=3,
        db_url=db_url,
    )

    semantic = None
    if result.success and payload.run_semantic_check and result.rows:
        try:
            semantic = semantic_checker.check(
                question=payload.question,
                sql=result.sql,
                rows=result.rows,
                schema_context=schema_context,
            )
        except Exception:
            pass  # semantic check is best-effort

    query_id = _save_to_history(result, semantic, payload.question, schema_version)

    if not result.success:
        return QueryResponse(
            success=False,
            query_id=query_id,
            question=payload.question,
            sql=result.sql,
            iterations=result.iterations,
            latency_ms=result.latency_ms,
            error=result.error_trace or "Query failed after max retries.",
        )

    return QueryResponse(
        success=True,
        query_id=query_id,
        question=payload.question,
        sql=result.sql,
        rows=result.rows,
        row_count=result.row_count,
        columns=result.columns,
        truncated=result.truncated,
        reasoning=result.reasoning,
        confidence=result.confidence,
        iterations=result.iterations,
        latency_ms=result.latency_ms,
        semantic_score=semantic.score if semantic else None,
        semantic_note=semantic.explanation if semantic else None,
    )


class SavedQuery(BaseModel):
    id: int
    question: str
    created_at: str


@router.post("/saved", response_model=SavedQuery)
def save_query(payload: QueryRequest) -> SavedQuery:
    conn = psycopg2.connect(settings.database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO saved_queries (question) VALUES (%s) RETURNING id, created_at",
                (payload.question,),
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return SavedQuery(id=row[0], question=payload.question, created_at=row[1].isoformat())


@router.get("/saved", response_model=list[SavedQuery])
def list_saved() -> list[SavedQuery]:
    conn = psycopg2.connect(settings.database_url)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, question, created_at FROM saved_queries ORDER BY created_at DESC LIMIT 100")
            rows = cur.fetchall()
    finally:
        conn.close()
    return [SavedQuery(id=r[0], question=r[1], created_at=r[2].isoformat()) for r in rows]


@router.delete("/saved/{query_id}", status_code=204)
def delete_saved(query_id: int) -> None:
    conn = psycopg2.connect(settings.database_url)
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM saved_queries WHERE id = %s", (query_id,))
        conn.commit()
    finally:
        conn.close()


class HistoryEntry(BaseModel):
    id: int
    question: str
    final_sql: str | None
    success: bool
    iterations: int
    latency_ms: int | None
    semantic_score: int | None
    row_count: int | None
    created_at: str


class FeedbackPayload(BaseModel):
    query_id: int
    rating: int  # 1 = thumbs down, 5 = thumbs up
    comment: str | None = None


@router.post("/feedback", status_code=204)
def submit_feedback(payload: FeedbackPayload) -> None:
    if payload.rating not in (1, 5):
        return
    conn = psycopg2.connect(settings.database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO feedback (query_id, rating, comment) VALUES (%s, %s, %s)",
                (payload.query_id, payload.rating, payload.comment),
            )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


@router.get("/history", response_model=list[HistoryEntry])
def get_history(limit: int = Query(default=50, le=200)) -> list[HistoryEntry]:
    try:
        conn = psycopg2.connect(settings.database_url)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, question, final_sql, success, iterations,
                       latency_ms, semantic_score, row_count, created_at
                FROM query_history
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
        conn.close()
        return [
            HistoryEntry(
                id=r[0],
                question=r[1],
                final_sql=r[2],
                success=r[3],
                iterations=r[4],
                latency_ms=r[5],
                semantic_score=r[6],
                row_count=r[7],
                created_at=r[8].isoformat() if r[8] else "",
            )
            for r in rows
        ]
    except Exception:
        return []
