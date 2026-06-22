"""
Auth route tests using an in-memory SQLite database.

Overrides the get_db dependency so no real PostgreSQL connection is needed.
Covers: password hashing, JWT creation/decoding, register, login.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.auth import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from api.database import get_db
from api.main import app
from api.models import Feedback, QueryHistory, User  # registers models with Base

# ---------------------------------------------------------------------------
# In-memory SQLite engine shared across tests in this module
# ---------------------------------------------------------------------------

SQLITE_URL = "sqlite://"

# StaticPool forces all connections to share the same in-memory database,
# so tables created in setup are visible to the FastAPI endpoint under test.
_engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

# Only create SQLite-compatible tables; SchemaEmbedding uses pgvector Vector
# which SQLite cannot handle, so we create tables individually.
for _table in [User.__table__, QueryHistory.__table__, Feedback.__table__]:
    _table.create(bind=_engine, checkfirst=True)


def _override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        h = hash_password("mysecret")
        assert h != "mysecret"

    def test_verify_correct_password(self):
        h = hash_password("correct")
        assert verify_password("correct", h) is True

    def test_reject_wrong_password(self):
        h = hash_password("correct")
        assert verify_password("wrong", h) is False

    def test_two_hashes_of_same_password_differ(self):
        # bcrypt salts every hash
        assert hash_password("abc") != hash_password("abc")


# ---------------------------------------------------------------------------
# JWT creation and decoding
# ---------------------------------------------------------------------------

class TestJWT:
    def test_create_and_decode_round_trip(self):
        token = create_access_token({"sub": "42", "email": "test@example.com"})
        data = decode_token(token)
        assert data.user_id == 42
        assert data.email == "test@example.com"

    def test_invalid_token_raises(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            decode_token("not.a.valid.token")
        assert exc_info.value.status_code == 401

    def test_token_is_string(self):
        token = create_access_token({"sub": "1", "email": "a@b.com"})
        assert isinstance(token, str)
        assert len(token) > 20


# ---------------------------------------------------------------------------
# Register endpoint
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_returns_201_and_token(self):
        r = client.post("/auth/register", json={
            "email": "newuser@example.com",
            "password": "strongpass123",
        })
        assert r.status_code == 201
        body = r.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert len(body["access_token"]) > 20

    def test_duplicate_email_returns_400(self):
        client.post("/auth/register", json={
            "email": "dup@example.com",
            "password": "pass1",
        })
        r = client.post("/auth/register", json={
            "email": "dup@example.com",
            "password": "pass2",
        })
        assert r.status_code == 400
        assert "already exists" in r.json()["detail"]

    def test_invalid_email_returns_422(self):
        r = client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "pass",
        })
        assert r.status_code == 422

    def test_missing_password_returns_422(self):
        r = client.post("/auth/register", json={"email": "x@x.com"})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# Login endpoint
# ---------------------------------------------------------------------------

class TestLogin:
    def setup_method(self):
        client.post("/auth/register", json={
            "email": "loginuser@example.com",
            "password": "correctpass",
        })

    def test_login_with_correct_credentials(self):
        r = client.post("/auth/login", data={
            "username": "loginuser@example.com",
            "password": "correctpass",
        })
        assert r.status_code == 200
        body = r.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self):
        r = client.post("/auth/login", data={
            "username": "loginuser@example.com",
            "password": "wrongpass",
        })
        assert r.status_code == 401

    def test_login_unknown_email_returns_401(self):
        r = client.post("/auth/login", data={
            "username": "nobody@example.com",
            "password": "anything",
        })
        assert r.status_code == 401
