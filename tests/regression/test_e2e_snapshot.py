# tests/integration/test_e2e_snapshot.py
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.crud.user import get_user_by_email, create_user
from app.schemas.user import UserCreate
from app.services.prediction_service import prediction_service
# from app.core.dependencies import get_current_user
from app.core.dependencies import get_current_user

# 1) Stand up one in‐memory SQLite engine for the entire module:
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,            # ← share one connection for everything
)
TestingSessionLocal = sessionmaker(bind=engine)

# 2) Create all tables ONCE on that engine:
Base.metadata.create_all(bind=engine)

# 3) Pre‐create exactly one test user so we never hit UNIQUE twice:
db = TestingSessionLocal()
test_user = get_user_by_email(db, "snap@example.com")
if not test_user:
    uc = UserCreate(username="snap_user", email="snap@example.com")
    test_user = create_user(db, uc)
db.close()

# 4) Override get_db() to yield our TestingSessionLocal
def override_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_db

# 5) Override get_current_user() to always return our pre‐created test_user
app.dependency_overrides[get_current_user] = lambda: test_user

# 6) Set up the TestClient
client = TestClient(app)

# 7) (Re-use or rewrite your mocks+tests as before)
@pytest.fixture(autouse=True)
def mock_services(monkeypatch):
    async def fake_forecast(symbol, periods):
        return [{"ds": "2025-01-01T00:00:00", "yhat": 50.0 + i} for i in range(periods)]
    monkeypatch.setattr(prediction_service, "forecast", fake_forecast)

    from app.services.financial_data_service import FinancialDataService
    async def dummy_price(self, symbol):
        return {"05. price": "100.0"}
    monkeypatch.setattr(FinancialDataService, "get_stock_quote", dummy_price)

def test_end_to_end_snapshot(data_regression):
    # your existing steps 1–5 here, using the `client` above...
    pf = client.post("/portfolios/", json={"name": "SnapPF"}).json()
    data_regression.check(pf, basename="portfolio_create")
    # …
