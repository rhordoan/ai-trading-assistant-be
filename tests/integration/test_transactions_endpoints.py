# tests/integration/test_transactions_endpoints.py

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.db.session import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ———————————————
# Setup in-memory SQLite override
# ———————————————
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables once
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the override
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def auth_client(client):
    # 1) Request magic link
    resp = client.post("/auth/request-token", json={"email": "tx@user.com"})
    token = resp.json()["token"]
    # 2) Verify token → set cookie
    resp = client.get(f"/auth/verify-token?token={token}")
    client.cookies["access_token"] = resp.cookies.get("access_token")
    return client

def test_transaction_crud_flow(client):
    c = auth_client(client)

    # 1) Create a portfolio → now returns 201
    pf_resp = c.post("/portfolios/", json={"name": "Tx PF"})
    assert pf_resp.status_code == 201
    pf = pf_resp.json()
    pf_id = pf["id"]

    # 2) Add three buy transactions
    for i in range(3):
        r = c.post(
            f"/portfolios/{pf_id}/transactions",
            json={"symbol": "AAPL", "type": "buy", "quantity": 1, "price": 100 + i}
        )
        assert r.status_code == 201

    # 3) List with pagination
    page1 = c.get(f"/portfolios/{pf_id}/transactions?skip=0&limit=2")
    assert page1.status_code == 200
    assert len(page1.json()) == 2

    # 4) Update one transaction
    tx_id = page1.json()[0]["id"]
    upd = c.put(
        f"/portfolios/{pf_id}/transactions/{tx_id}",
        json={"price": 123.45}
    )
    assert upd.status_code == 200
    assert upd.json()["price"] == 123.45

    # 5) Delete that transaction
    dl = c.delete(f"/portfolios/{pf_id}/transactions/{tx_id}")
    assert dl.status_code == 204

    # 6) Ensure it’s gone
    remaining = c.get(f"/portfolios/{pf_id}/transactions")
    assert all(tx["id"] != tx_id for tx in remaining.json())
