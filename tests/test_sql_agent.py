"""
Tests for the SQL agent pipeline.

Validator and corrector tests run without a database connection.
Generator tests are skipped if GROQ_API_KEY is not set.
"""

from __future__ import annotations

from sql_agent.corrector import CorrectionAttempt, CorrectionResult
from sql_agent.executor import ExecutionResult
from sql_agent.validator import ValidationResult, validate

# ---------------------------------------------------------------------------
# Validator tests
# ---------------------------------------------------------------------------

class TestValidator:
    def test_valid_select(self):
        result = validate("SELECT id, name FROM customers WHERE id = 1")
        assert result.is_valid is True
        assert result.error_message == ""

    def test_valid_select_with_join(self):
        sql = (
            "SELECT c.name, o.total FROM customers c "
            "JOIN orders o ON c.id = o.customer_id LIMIT 10"
        )
        result = validate(sql)
        assert result.is_valid is True

    def test_valid_select_with_aggregate(self):
        sql = "SELECT region, SUM(sales) AS total_sales FROM orders GROUP BY region ORDER BY total_sales DESC"
        result = validate(sql)
        assert result.is_valid is True

    def test_rejects_empty_string(self):
        result = validate("")
        assert result.is_valid is False
        assert "Empty" in result.error_message

    def test_rejects_whitespace_only(self):
        result = validate("   ")
        assert result.is_valid is False

    def test_rejects_insert(self):
        result = validate("INSERT INTO customers (name) VALUES ('evil')")
        assert result.is_valid is False
        assert "INSERT" in result.error_message or "allowed" in result.error_message

    def test_rejects_drop(self):
        result = validate("DROP TABLE customers")
        assert result.is_valid is False

    def test_rejects_delete(self):
        result = validate("DELETE FROM customers WHERE id = 1")
        assert result.is_valid is False

    def test_rejects_update(self):
        result = validate("UPDATE customers SET name = 'x' WHERE id = 1")
        assert result.is_valid is False

    def test_syntax_error(self):
        result = validate("SELECT FROM WHERE")
        assert result.is_valid is False

    def test_subquery_is_valid(self):
        sql = "SELECT * FROM (SELECT id, name FROM customers) AS sub WHERE id > 10"
        result = validate(sql)
        assert result.is_valid is True

    def test_cte_is_valid(self):
        sql = (
            "WITH top_customers AS (SELECT customer_id, SUM(amount) AS total "
            "FROM orders GROUP BY customer_id) "
            "SELECT customer_id, total FROM top_customers ORDER BY total DESC LIMIT 5"
        )
        result = validate(sql)
        assert result.is_valid is True


# ---------------------------------------------------------------------------
# Corrector dataclass / plumbing tests (no LLM or DB calls)
# ---------------------------------------------------------------------------


class TestCorrectionResult:
    def test_default_success_fields(self):
        r = CorrectionResult(success=True, sql="SELECT 1", iterations=1)
        assert r.rows == []
        assert r.error_trace == ""
        assert r.truncated is False

    def test_failure_result_has_no_rows(self):
        r = CorrectionResult(success=False, sql="", iterations=3, error_trace="oops")
        assert not r.success
        assert r.rows == []

    def test_attempt_stores_fields(self):
        val = ValidationResult(is_valid=False, error_message="syntax error")
        exec_res = ExecutionResult(success=False, error_message="timeout")
        attempt = CorrectionAttempt(
            iteration=1, sql="SELECT bad", validation=val,
            execution=exec_res, error="syntax error",
        )
        assert attempt.iteration == 1
        assert attempt.error == "syntax error"

    def test_execution_result_truncated_flag(self):
        r = ExecutionResult(success=True, rows=[{"x": 1}], row_count=1, truncated=True)
        assert r.truncated is True
