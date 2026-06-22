"""
Tests for POST /api/query with a mocked self-corrector.

No real LLM or database calls are made. The corrector and assembler are
patched so we can test routing logic, response shape, and error handling.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from api.main import app
from sql_agent.corrector import CorrectionResult

client = TestClient(app)

_MOCK_CONTEXT = "=== RELEVANT SCHEMA CONTEXT ===\nUser question: test\n=== END SCHEMA CONTEXT ==="


def _make_success_result(**kwargs) -> CorrectionResult:
    defaults = dict(
        success=True,
        sql="SELECT contact_name FROM nw_customers LIMIT 5",
        rows=[{"contact_name": "Maria Anders"}],
        row_count=1,
        columns=["contact_name"],
        truncated=False,
        reasoning="Used nw_customers table.",
        confidence=0.95,
        iterations=1,
        latency_ms=800,
        error_trace="",
    )
    defaults.update(kwargs)
    return CorrectionResult(**defaults)


def _make_failure_result(**kwargs) -> CorrectionResult:
    defaults = dict(
        success=False,
        sql="SELECT bad FROM nowhere",
        rows=[],
        row_count=0,
        columns=[],
        truncated=False,
        reasoning="",
        confidence=0.0,
        iterations=3,
        latency_ms=4500,
        error_trace="[iter 1] execution error: relation 'nowhere' does not exist",
    )
    defaults.update(kwargs)
    return CorrectionResult(**defaults)


class TestQueryEndpointShape:
    @patch("api.routes.query_routes._save_to_history")
    @patch("api.routes.query_routes.semantic_checker.check")
    @patch("api.routes.query_routes._get_corrector")
    @patch("api.routes.query_routes._get_assembler")
    def test_successful_query_returns_200(self, mock_asm, mock_corr, mock_sem, mock_save):
        mock_asm.return_value.assemble.return_value = _MOCK_CONTEXT
        mock_corr.return_value.run.return_value = _make_success_result()
        mock_sem.return_value = MagicMock(score=9, explanation="Looks correct.", passed=True)

        r = client.post("/api/query", json={"question": "List all customers"})
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert "sql" in body
        assert "rows" in body
        assert "row_count" in body
        assert "iterations" in body
        assert "latency_ms" in body
        assert "semantic_score" in body

    @patch("api.routes.query_routes._save_to_history")
    @patch("api.routes.query_routes._get_corrector")
    @patch("api.routes.query_routes._get_assembler")
    def test_failed_query_returns_200_with_success_false(self, mock_asm, mock_corr, mock_save):
        mock_asm.return_value.assemble.return_value = _MOCK_CONTEXT
        mock_corr.return_value.run.return_value = _make_failure_result()

        r = client.post("/api/query", json={"question": "Show me broken SQL"})
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is False
        assert body["error"] is not None
        assert body["iterations"] == 3

    @patch("api.routes.query_routes._save_to_history")
    @patch("api.routes.query_routes._get_corrector")
    @patch("api.routes.query_routes._get_assembler")
    def test_semantic_score_included_in_response(self, mock_asm, mock_corr, mock_save):
        mock_asm.return_value.assemble.return_value = _MOCK_CONTEXT
        mock_corr.return_value.run.return_value = _make_success_result()

        with patch("api.routes.query_routes.semantic_checker.check") as mock_sem:
            mock_sem.return_value = MagicMock(score=8, explanation="Good query.", passed=True)
            r = client.post("/api/query", json={"question": "Show customers", "run_semantic_check": True})

        assert r.status_code == 200
        body = r.json()
        assert body["semantic_score"] == 8
        assert body["semantic_note"] == "Good query."

    @patch("api.routes.query_routes._save_to_history")
    @patch("api.routes.query_routes._get_corrector")
    @patch("api.routes.query_routes._get_assembler")
    def test_semantic_check_skipped_when_disabled(self, mock_asm, mock_corr, mock_save):
        mock_asm.return_value.assemble.return_value = _MOCK_CONTEXT
        mock_corr.return_value.run.return_value = _make_success_result()

        with patch("api.routes.query_routes.semantic_checker.check") as mock_sem:
            r = client.post("/api/query", json={
                "question": "Show customers",
                "run_semantic_check": False,
            })
            mock_sem.assert_not_called()

        assert r.status_code == 200
        body = r.json()
        assert body["semantic_score"] is None


class TestQueryEndpointValidation:
    def test_question_too_short_returns_422(self):
        r = client.post("/api/query", json={"question": "hi"})
        assert r.status_code == 422

    def test_missing_question_returns_422(self):
        r = client.post("/api/query", json={})
        assert r.status_code == 422

    def test_question_too_long_returns_422(self):
        r = client.post("/api/query", json={"question": "x" * 1001})
        assert r.status_code == 422

    def test_default_schema_version_is_v1(self):
        # When schema_version is not provided, the default should be v1
        with (
            patch("api.routes.query_routes._get_assembler") as mock_asm,
            patch("api.routes.query_routes._get_corrector") as mock_corr,
            patch("api.routes.query_routes._save_to_history"),
            patch("api.routes.query_routes.semantic_checker.check") as mock_sem,
        ):
            mock_asm.return_value.assemble.return_value = _MOCK_CONTEXT
            mock_corr.return_value.run.return_value = _make_success_result()
            mock_sem.return_value = MagicMock(score=9, explanation="ok", passed=True)

            client.post("/api/query", json={"question": "Show customers"})
            call_kwargs = mock_asm.return_value.assemble.call_args
            assert call_kwargs.kwargs.get("schema_version") == "v1"
