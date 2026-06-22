"""
SQL generator using Groq (llama-3.3-70b-versatile).

Takes an assembled schema context and a user question, builds a prompt,
and returns structured output: {sql, reasoning, confidence}.
Supports multi-turn correction by accepting an existing message history.
"""

from __future__ import annotations

import json
from typing import Any

from groq import Groq

from api.config import settings


MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.1  # low for deterministic SQL

SYSTEM_PROMPT = """You are an expert SQL analyst working with PostgreSQL.

Your job is to convert a natural language question into a correct SQL SELECT statement
using the schema context provided. Follow these rules strictly:

1. Only generate SELECT statements. Never write INSERT, UPDATE, DELETE, DROP, or any DDL.
2. Use the exact table and column names from the schema context.
3. Apply the JOIN clauses shown in the schema context when connecting multiple tables.
4. CRITICAL: Tables are grouped by database. The context will show which database each
   table belongs to. NEVER join tables from different databases. Tables with prefix nw_
   belong to Northwind, tpch_ to TPC-H, and nyc_ to NYC Taxi. Pick ONE database per query.
5. Pay close attention to the column disambiguation notes if present.
6. If the question mentions time ranges like "last month" or "recent", use sensible defaults.
7. Always return valid PostgreSQL syntax.

Respond with a JSON object containing exactly these fields:
{
  "sql": "the complete SELECT statement",
  "reasoning": "brief explanation of which tables/joins you used and why",
  "confidence": 0.95
}

Confidence is a float from 0.0 to 1.0 reflecting how certain you are the SQL is correct."""


class GenerationResult:
    def __init__(self, sql: str, reasoning: str, confidence: float, raw: str) -> None:
        self.sql = sql
        self.reasoning = reasoning
        self.confidence = confidence
        self.raw = raw


class SQLGenerator:
    def __init__(self, groq_api_key: str | None = None) -> None:
        self.client = Groq(api_key=groq_api_key or settings.groq_api_key)

    def build_initial_messages(self, question: str, schema_context: str) -> list[dict[str, Any]]:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"{schema_context}\n\n"
                    f"Question: {question}\n\n"
                    "Generate the SQL query as a JSON object."
                ),
            },
        ]

    def append_error_to_messages(
        self,
        messages: list[dict[str, Any]],
        failed_sql: str,
        error: str,
    ) -> list[dict[str, Any]]:
        messages = messages.copy()
        messages.append({
            "role": "user",
            "content": (
                f"The SQL you generated failed with this error:\n\n"
                f"SQL:\n{failed_sql}\n\n"
                f"Error:\n{error}\n\n"
                "Please fix the SQL and return the corrected version as a JSON object."
            ),
        })
        return messages

    def generate(self, messages: list[dict[str, Any]]) -> GenerationResult:
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=TEMPERATURE,
        )
        raw = response.choices[0].message.content
        parsed = json.loads(raw)
        return GenerationResult(
            sql=parsed.get("sql", "").strip(),
            reasoning=parsed.get("reasoning", ""),
            confidence=float(parsed.get("confidence", 0.0)),
            raw=raw,
        )
