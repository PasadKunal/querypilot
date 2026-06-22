"""
Sandboxed SQL execution using the querypilot_sandbox read-only role.

Applies a 10-second query timeout and caps results at 1,000 rows.
Returns rows as a list of dicts so the API layer can serialize them easily.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import psycopg2
import psycopg2.extras

from api.config import settings

MAX_ROWS = 1_000
TIMEOUT_MS = 10_000  # 10 seconds, enforced by postgres statement_timeout


@dataclass
class ExecutionResult:
    success: bool
    rows: list[dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    columns: list[str] = field(default_factory=list)
    error_message: str = ""
    truncated: bool = False


def execute(sql: str, db_url: str | None = None) -> ExecutionResult:
    """
    Run sql in a read-only sandbox connection.
    The SQL is wrapped in a subquery with LIMIT so the planner still
    sees the full query cost but we only fetch at most MAX_ROWS rows.
    """
    effective_url = db_url or settings.sandbox_database_url
    wrapped_sql = f"SELECT * FROM ({sql}) AS _qp_result LIMIT {MAX_ROWS + 1}"

    try:
        conn = psycopg2.connect(effective_url, options=f"-c statement_timeout={TIMEOUT_MS}")
    except Exception as exc:
        return ExecutionResult(success=False, error_message=f"Connection failed: {exc}")

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(wrapped_sql)
            raw_rows = cur.fetchall()
            columns = [desc.name for desc in cur.description] if cur.description else []
    except psycopg2.Error as exc:
        return ExecutionResult(success=False, error_message=str(exc).strip())
    except Exception as exc:
        return ExecutionResult(success=False, error_message=f"Unexpected error: {exc}")
    finally:
        conn.close()

    truncated = len(raw_rows) > MAX_ROWS
    rows = [dict(r) for r in raw_rows[:MAX_ROWS]]
    return ExecutionResult(
        success=True,
        rows=rows,
        row_count=len(rows),
        columns=columns,
        truncated=truncated,
    )
