"""
Semantic validation after successful SQL execution.

Asks the LLM: given this question, schema, SQL, and a sample of results,
does this SQL correctly answer the question? Returns a score 1-10.
Scores below 7 are flagged as potentially incorrect.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from groq import Groq

from api.config import settings


MODEL = "llama-3.3-70b-versatile"
SEMANTIC_PASS_THRESHOLD = 7
SAMPLE_ROWS = 5

SYSTEM_PROMPT = """You are a SQL quality reviewer. You will be given:
- A natural language question
- The SQL query that was generated to answer it
- A small sample of the query results

Your task: decide whether the SQL correctly answers the question.

Respond with a JSON object:
{
  "score": 8,
  "explanation": "The SQL correctly identifies top customers by revenue using the right join and aggregation."
}

Score 1-10. Score 7 or above means the SQL correctly answers the question.
Score below 7 means there is a likely mistake (wrong table, wrong aggregation, missing filter, etc.)."""


@dataclass
class SemanticCheckResult:
    score: int
    explanation: str
    passed: bool


def check(
    question: str,
    sql: str,
    rows: list[dict[str, Any]],
    schema_context: str,
    groq_api_key: str | None = None,
) -> SemanticCheckResult:
    client = Groq(api_key=groq_api_key or settings.groq_api_key)

    sample = rows[:SAMPLE_ROWS]
    sample_text = json.dumps(sample, indent=2, default=str)

    user_content = (
        f"Question: {question}\n\n"
        f"SQL:\n{sql}\n\n"
        f"Result sample ({len(sample)} of {len(rows)} rows):\n{sample_text}\n\n"
        "Does this SQL correctly answer the question? Respond with JSON."
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    raw = response.choices[0].message.content
    parsed = json.loads(raw)
    score = int(parsed.get("score", 0))
    explanation = parsed.get("explanation", "")
    return SemanticCheckResult(
        score=score,
        explanation=explanation,
        passed=score >= SEMANTIC_PASS_THRESHOLD,
    )
