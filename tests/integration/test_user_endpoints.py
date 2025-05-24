import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_current_user
from app.db.session import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app.dependency_overrides.pop(get_current_user, None)

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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

def test_full_auth_and_user_flow(client):
    app.dependency_overrides.pop(get_current_user, None)

    # 1) Request magic link
    resp1 = client.post("/auth/request-token", json={"email": "bob@example.com"})
    assert resp1.status_code == 200
    token = resp1.json()["token"]

    # 2) Verify token & set cookie
    resp2 = client.get(f"/auth/verify-token?token={token}")
    assert resp2.status_code == 200
    assert "access_token" in resp2.cookies

    # 3) Create a new user (uses the real get_current_user now)
    client.cookies["access_token"] = resp2.cookies["access_token"]
    resp3 = client.post(
        "/users/",
        json={"username": "bob", "email": "bob@example.com"}
    )
    assert resp3.status_code == 201
    u = resp3.json()
    assert u["username"] == "bob"
    user_id = u["id"]

    # 4) Read /users/ and /users/{id}
    list_resp = client.get("/users/")
    assert list_resp.status_code == 200
    assert any(u["id"] == user_id for u in list_resp.json())

    get_resp = client.get(f"/users/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == "bob@example.com"

    # 5) Read current user
    me_resp = client.get("/users/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "bob"

    # 6) Update user
    upd_resp = client.put(
        f"/users/{user_id}",
        json={"full_name": "Bobby"}
    )
    assert upd_resp.status_code == 200
    assert upd_resp.json()["full_name"] == "Bobby"

    # 7) Delete user
    del_resp = client.delete(f"/users/{user_id}")
    assert del_resp.status_code == 204

    # 8) Now /users/{id} should 404
    assert client.get(f"/users/{user_id}").status_code == 404
