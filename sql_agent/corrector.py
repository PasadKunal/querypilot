"""
3-iteration self-correction loop.

Flow per iteration:
  1. Generate SQL (Groq llama-3.3-70b)
  2. Validate syntax (sqlglot)
  3. Execute in read-only sandbox
  If any step fails, feed the error back into the LLM and retry.
  Stop on first success or after max_iterations attempts.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from sql_agent.executor import ExecutionResult, execute
from sql_agent.generator import GenerationResult, SQLGenerator
from sql_agent.validator import ValidationResult, validate

MAX_ITERATIONS = 3


@dataclass
class CorrectionAttempt:
    iteration: int
    sql: str
    validation: ValidationResult
    execution: ExecutionResult | None
    error: str


@dataclass
class CorrectionResult:
    success: bool
    sql: str = ""
    rows: list[dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    columns: list[str] = field(default_factory=list)
    truncated: bool = False
    reasoning: str = ""
    confidence: float = 0.0
    iterations: int = 0
    latency_ms: int = 0
    attempts: list[CorrectionAttempt] = field(default_factory=list)
    error_trace: str = ""


class SelfCorrector:
    def __init__(self, generator: SQLGenerator | None = None) -> None:
        self.generator = generator or SQLGenerator()

    def run(
        self,
        question: str,
        schema_context: str,
        max_iterations: int = MAX_ITERATIONS,
        db_url: str | None = None,
    ) -> CorrectionResult:
        start = time.perf_counter()
        messages = self.generator.build_initial_messages(question, schema_context)
        attempts: list[CorrectionAttempt] = []
        error_trace_parts: list[str] = []
        gen_result: GenerationResult | None = None
        exec_result: ExecutionResult | None = None

        for i in range(1, max_iterations + 1):
            gen_result = self.generator.generate(messages)
            sql = gen_result.sql

            val_result = validate(sql)
            if not val_result.is_valid:
                attempts.append(CorrectionAttempt(
                    iteration=i, sql=sql, validation=val_result,
                    execution=None, error=val_result.error_message,
                ))
                error_trace_parts.append(f"[iter {i}] syntax error: {val_result.error_message}")
                messages = self.generator.append_error_to_messages(messages, sql, val_result.error_message)
                continue

            exec_result = execute(sql, db_url=db_url)
            if not exec_result.success:
                attempts.append(CorrectionAttempt(
                    iteration=i, sql=sql, validation=val_result,
                    execution=exec_result, error=exec_result.error_message,
                ))
                error_trace_parts.append(f"[iter {i}] execution error: {exec_result.error_message}")
                messages = self.generator.append_error_to_messages(messages, sql, exec_result.error_message)
                continue

            # Success
            latency_ms = int((time.perf_counter() - start) * 1000)
            return CorrectionResult(
                success=True,
                sql=sql,
                rows=exec_result.rows,
                row_count=exec_result.row_count,
                columns=exec_result.columns,
                truncated=exec_result.truncated,
                reasoning=gen_result.reasoning,
                confidence=gen_result.confidence,
                iterations=i,
                latency_ms=latency_ms,
                attempts=attempts,
                error_trace="; ".join(error_trace_parts),
            )

        latency_ms = int((time.perf_counter() - start) * 1000)
        last_sql = gen_result.sql if gen_result else ""
        return CorrectionResult(
            success=False,
            sql=last_sql,
            iterations=max_iterations,
            latency_ms=latency_ms,
            attempts=attempts,
            error_trace="; ".join(error_trace_parts),
            reasoning=gen_result.reasoning if gen_result else "",
            confidence=gen_result.confidence if gen_result else 0.0,
        )
