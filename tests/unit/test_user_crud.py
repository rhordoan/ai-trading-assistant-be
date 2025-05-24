import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.crud import user as crud_user
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import TradingExperienceLevel, RiskAppetite, InvestmentGoals

@pytest.fixture(scope="module")
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    yield session
    session.close()

def test_create_get_update_delete_user(db):
    # 1) Create
    u_in = UserCreate(username="alice", email="alice@example.com")
    u = crud_user.create_user(db, u_in)
    assert u.id is not None
    assert u.username == "alice"
    assert u.email == "alice@example.com"

    # 2) Get by email/username
    by_email = crud_user.get_user_by_email(db, "alice@example.com")
    assert by_email.id == u.id
    by_usern = crud_user.get_user_by_username(db, "alice")
    assert by_usern.id == u.id

    # 3) Update some fields
    upd = UserUpdate(full_name="Alice A.", timezone="Europe/Bucharest",
                     trading_experience=TradingExperienceLevel.INTERMEDIATE,
                     risk_appetite=RiskAppetite.MEDIUM,
                     investment_goals=InvestmentGoals.Long_term_Growth)
    u2 = crud_user.update_user(db, u, upd)
    assert u2.full_name == "Alice A."
    assert u2.timezone == "Europe/Bucharest"
    assert u2.trading_experience == TradingExperienceLevel.INTERMEDIATE

    # 4) Delete
    crud_user.delete_user(db, u2)
    assert crud_user.get_user(db, u2.id) is None
