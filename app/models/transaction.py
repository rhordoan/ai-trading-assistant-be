# app/models/transaction.py

from datetime import date
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base

class TransactionType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"

class Transaction(Base):
    __tablename__ = "transactions"

    id           = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(
        Integer,
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
    )
    symbol    = Column(String(20), nullable=False)
    type      = Column(Enum(TransactionType), nullable=False)
    quantity  = Column(Float, nullable=False)
    price     = Column(Float, nullable=False)
    # new: explicit trade date (defaults to today if omitted)
    date      = Column(Date, nullable=False, default=date.today)
    # existing: insertion timestamp
    timestamp = Column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False,
    )

    portfolio = relationship("Portfolio", back_populates="transactions")
