"""
SQL syntax validation using sqlglot.

Parses the generated SQL before touching the database. Catches syntax
errors early and rejects non-SELECT statements as a safety guard.
"""

from __future__ import annotations

from dataclasses import dataclass

import sqlglot
import sqlglot.errors


@dataclass
class ValidationResult:
    is_valid: bool
    error_message: str = ""


_ALLOWED_STATEMENT_TYPES = {"Select"}


def validate(sql: str) -> ValidationResult:
    if not sql or not sql.strip():
        return ValidationResult(is_valid=False, error_message="Empty SQL string.")

    try:
        statements = sqlglot.parse(sql, dialect="postgres")
    except sqlglot.errors.ParseError as exc:
        return ValidationResult(is_valid=False, error_message=f"Syntax error: {exc}")

    if not statements:
        return ValidationResult(is_valid=False, error_message="No SQL statement found.")

    for stmt in statements:
        stmt_type = type(stmt).__name__
        if stmt_type not in _ALLOWED_STATEMENT_TYPES:
            return ValidationResult(
                is_valid=False,
                error_message=(
                    f"Only SELECT statements are allowed. Got: {stmt_type}. "
                    "Never generate INSERT, UPDATE, DELETE, DROP, or DDL."
                ),
            )

    return ValidationResult(is_valid=True)
