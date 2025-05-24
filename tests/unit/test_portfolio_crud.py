import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.crud import portfolio as crud_pf
from app.schemas.portfolio import PortfolioCreate

# Fixture: sesiune DB in-memory
@pytest.fixture(scope="module")
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    yield session
    session.close()

def test_create_and_get_portfolio(db):
    # creare
    p_in = PortfolioCreate(name="Test PF")
    p = crud_pf.create_portfolio(db, user_id=1, data=p_in)
    assert p.id is not None
    assert p.name == "Test PF"
    assert p.user_id == 1

    # listare
    all_p = crud_pf.get_portfolios(db, user_id=1)
    assert len(all_p) == 1
    assert all_p[0].id == p.id

def test_get_nonexistent_portfolio(db):
    p = crud_pf.get_portfolio(db, portfolio_id=999)
    assert p is None
