import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.crud import portfolio as crud_pf, transaction as crud_tx
from app.schemas.portfolio import PortfolioCreate
from app.schemas.transaction import TransactionCreate

@pytest.fixture(scope="module")
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    yield session
    session.close()

@pytest.fixture(scope="module")
def portfolio(db):
    p = crud_pf.create_portfolio(db, user_id=1, data=PortfolioCreate(name="PF for Tx"))
    return p

def test_create_and_get_transactions(db, portfolio):
    # Adding 3 transactions
    tx_in = TransactionCreate(symbol="AAPL", type="buy", quantity=2, price=100.0)
    for _ in range(3):
        tx = crud_tx.create_transaction(db, portfolio_id=portfolio.id, tx_in=tx_in)
        assert tx.id is not None
        assert tx.symbol == "AAPL"

    # Listing transactions without filters
    txs = crud_tx.get_transactions(db, portfolio_id=portfolio.id, skip=0, limit=10)
    assert len(txs) == 3

def test_update_transaction(db, portfolio):
    txs = crud_tx.get_transactions(db, portfolio_id=portfolio.id)
    tx0 = txs[0]
    updated = crud_tx.update_transaction(db, tx_id=tx0.id, tx_in={"price": 120.0})
    assert updated.price == 120.0

def test_delete_transaction(db, portfolio):
    txs = crud_tx.get_transactions(db, portfolio_id=portfolio.id)
    tx_id = txs[0].id
    result = crud_tx.delete_transaction(db, tx_id=tx_id)
    assert result is True
    # Check if the transaction is actually deleted
    remaining = crud_tx.get_transactions(db, portfolio_id=portfolio.id)
    assert all(tx.id != tx_id for tx in remaining)
