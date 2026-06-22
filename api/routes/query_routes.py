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
from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.config import settings
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


class QueryResponse(BaseModel):
    success: bool
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


def _save_to_history(result, semantic, question: str, schema_version: str) -> None:
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
        conn.commit()
        conn.close()
    except Exception:
        pass  # history is best-effort; never fail the user response


@router.post("/query", response_model=QueryResponse)
def run_query(payload: QueryRequest) -> QueryResponse:
    assembler = _get_assembler()
    corrector = _get_corrector()

    schema_context = assembler.assemble(
        query=payload.question,
        schema_version=payload.schema_version,
    )

    result = corrector.run(
        question=payload.question,
        schema_context=schema_context,
        max_iterations=3,
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

    _save_to_history(result, semantic, payload.question, payload.schema_version)

    if not result.success:
        return QueryResponse(
            success=False,
            question=payload.question,
            sql=result.sql,
            iterations=result.iterations,
            latency_ms=result.latency_ms,
            error=result.error_trace or "Query failed after max retries.",
        )

    return QueryResponse(
        success=True,
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
