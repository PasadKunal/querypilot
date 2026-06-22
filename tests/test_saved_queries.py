"""
Tests for saved queries endpoints.

POST /api/saved   save a question
GET  /api/saved   list saved questions
DELETE /api/saved/{id}  remove one
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def _mock_conn(fetchone=None, fetchall=None):
    conn = MagicMock()
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    if fetchone is not None:
        cur.fetchone.return_value = fetchone
    if fetchall is not None:
        cur.fetchall.return_value = fetchall
    conn.cursor.return_value = cur
    return conn


@patch("psycopg2.connect")
class TestSavedQueries:
    def test_save_question(self, mock_connect):
        ts = datetime(2025, 1, 1, tzinfo=timezone.utc)
        mock_connect.return_value = _mock_conn(fetchone=(7, ts))
        res = client.post(
            "/api/saved",
            json={"question": "Show top 5 customers by revenue"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["id"] == 7
        assert "customers" in body["question"]

    def test_list_saved_returns_list(self, mock_connect):
        ts = datetime(2025, 1, 1, tzinfo=timezone.utc)
        mock_connect.return_value = _mock_conn(fetchall=[
            (1, "How many orders per region?", ts),
        ])
        res = client.get("/api/saved")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert data[0]["id"] == 1

    def test_delete_saved(self, mock_connect):
        mock_connect.return_value = _mock_conn()
        res = client.delete("/api/saved/1")
        assert res.status_code == 204

    def test_empty_list_when_no_saves(self, mock_connect):
        mock_connect.return_value = _mock_conn(fetchall=[])
        res = client.get("/api/saved")
        assert res.json() == []
