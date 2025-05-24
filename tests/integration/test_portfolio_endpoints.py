# tests/integration/test_portfolio_endpoints.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db

# ———————————————
# Setup in-memory DB override
# ———————————————
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def auth_client(client):
    # helper to login & set cookie
    token = client.post("/auth/request-token", json={"email": "pf@user.com"}).json()["token"]
    res = client.get(f"/auth/verify-token?token={token}")
    client.cookies["access_token"] = res.cookies["access_token"]
    return client

def test_portfolio_crud_and_value(client):
    c = auth_client(client)

    resp = c.post("/portfolios/", json={"name": "Integration PF"})
    assert resp.status_code == 201        
    pf = resp.json()
    pf_id = pf["id"]

    lst = c.get("/portfolios/")
    assert lst.status_code == 200
    assert any(p["id"] == pf_id for p in lst.json())

    val = c.get(f"/portfolios/{pf_id}/value")
    assert val.status_code == 200
    assert val.json()["value"] == 0.0
