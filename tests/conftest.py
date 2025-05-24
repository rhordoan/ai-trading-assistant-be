# tests/conftest.py
import os
import pytest
from fastapi.testclient import TestClient

# 1) Tell our code to use an in-memory SQLite before any imports
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from app.main import app    # safe: no DB work at import
client = TestClient(app)

@pytest.fixture(scope="session")
def test_client():
    return client
