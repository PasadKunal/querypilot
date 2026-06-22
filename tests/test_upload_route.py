"""
Tests for POST /api/tables/upload, GET /api/tables, and DELETE /api/tables/{name}.

All psycopg2 and Gemini calls are patched so no real database or network
traffic is required.
"""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

SAMPLE_CSV = b"product,price,in_stock\nWidget,9.99,true\nGadget,19.99,false\n"


def _auth_header() -> dict[str, str]:
    from api.auth import create_access_token
    token = create_access_token({"sub": "99", "email": "tester@example.com"})
    return {"Authorization": f"Bearer {token}"}


def _mock_conn():
    conn = MagicMock()
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchone.return_value = ("ut_abc_products", "2025-01-01 00:00:00+00")
    cur.fetchall.return_value = []
    conn.cursor.return_value = cur
    return conn


@patch("api.routes.upload_routes._embed_texts", return_value=[[0.0] * 768, [0.0] * 768, [0.0] * 768, [0.0] * 768])
@patch("psycopg2.extras.execute_batch")
@patch("psycopg2.connect")
class TestUploadCSV:
    def test_valid_csv_returns_200(self, mock_connect, mock_batch, mock_embed):
        mock_connect.return_value = _mock_conn()
        res = client.post(
            "/api/tables/upload",
            files={"file": ("data.csv", io.BytesIO(SAMPLE_CSV), "text/csv")},
            headers=_auth_header(),
        )
        assert res.status_code == 200
        body = res.json()
        assert body["column_count"] == 3
        assert body["row_count"] == 2

    def test_non_csv_rejected(self, mock_connect, mock_batch, mock_embed):
        res = client.post(
            "/api/tables/upload",
            files={"file": ("data.json", io.BytesIO(b"{}"), "application/json")},
            headers=_auth_header(),
        )
        assert res.status_code == 400

    def test_unauthenticated_upload_rejected(self, mock_connect, mock_batch, mock_embed):
        res = client.post(
            "/api/tables/upload",
            files={"file": ("data.csv", io.BytesIO(SAMPLE_CSV), "text/csv")},
        )
        assert res.status_code == 401

    def test_empty_csv_returns_422(self, mock_connect, mock_batch, mock_embed):
        empty = b"name,age\n"
        res = client.post(
            "/api/tables/upload",
            files={"file": ("empty.csv", io.BytesIO(empty), "text/csv")},
            headers=_auth_header(),
        )
        assert res.status_code == 422


@patch("psycopg2.connect")
class TestListTables:
    def test_returns_list(self, mock_connect):
        mock_connect.return_value = _mock_conn()
        res = client.get("/api/tables")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


@patch("psycopg2.connect")
class TestDeleteTable:
    def test_valid_table_name_accepted(self, mock_connect):
        mock_connect.return_value = _mock_conn()
        res = client.delete(
            "/api/tables/ut_ab12cd34_sales",
            headers=_auth_header(),
        )
        assert res.status_code == 204

    def test_invalid_table_name_rejected(self, mock_connect):
        res = client.delete(
            "/api/tables/nw_customers",
            headers=_auth_header(),
        )
        assert res.status_code == 400

    def test_unauthenticated_delete_rejected(self, mock_connect):
        res = client.delete("/api/tables/ut_ab12cd34_sales")
        assert res.status_code == 401
