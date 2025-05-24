import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.prediction_service import prediction_service

# ———————————————
# DB override
# ———————————————
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = lambda: TestingSessionLocal()

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_forecast_monkeypatched(client, monkeypatch):
    async def fake_forecast(symbol, periods):
        return [{"ds": "2025-01-01T00:00:00", "yhat": 100.0 + i} for i in range(periods)]
    monkeypatch.setattr(prediction_service, "forecast", fake_forecast)

    res = client.get("/forecast/GOOGL?periods=5")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 5
    assert data[0]["yhat"] == 100.0
