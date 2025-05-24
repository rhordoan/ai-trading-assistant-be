from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    name        = Column(String(100), nullable=False)
    created_at  = Column(DateTime(timezone=False), server_default=func.now())

    positions    = relationship("Position", back_populates="portfolio")
    transactions = relationship("Transaction", back_populates="portfolio")


class Position(Base):
    __tablename__ = "positions"

    id           = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol       = Column(String(20), nullable=False)
    quantity     = Column(Float, nullable=False)
    avg_price    = Column(Float, nullable=False)
    created_at   = Column(DateTime(timezone=False), server_default=func.now())

    portfolio    = relationship("Portfolio", back_populates="positions")
