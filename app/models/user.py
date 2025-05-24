from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
from enum import Enum

from app.db.session import Base

class TradingExperienceLevel(str, Enum):
    BEGINNER     = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED     = "Advanced"
    PROFESSIONAL = "Professional"

class RiskAppetite(str, Enum):
    LOW       = "Low"
    MEDIUM    = "Medium"
    HIGH      = "High"
    VERY_HIGH = "Very High"

class InvestmentGoals(str, Enum):
    Short_term_Gains     = "Short-term Gains"
    Long_term_Growth     = "Long-term Growth"
    Income_Generation    = "Income Generation"
    Capital_Preservation = "Capital Preservation"
    Speculation          = "Speculation"

class User(Base):
    __tablename__ = "users"

    id                      = Column(Integer, primary_key=True, index=True)
    username                = Column(String(50), unique=True, index=True, nullable=False)
    email                   = Column(String(100), unique=True, index=True, nullable=False)
    full_name               = Column(String(100), nullable=True)
    profile_picture_url     = Column(String(255), nullable=True)
    is_active               = Column(Boolean, default=True)
    trading_experience      = Column(SAEnum(TradingExperienceLevel), nullable=True)
    risk_appetite           = Column(SAEnum(RiskAppetite), nullable=True)
    investment_goals        = Column(SAEnum(InvestmentGoals), nullable=True)
    preferred_asset_classes = Column(JSON, nullable=True)
    interests_for_feed      = Column(JSON, nullable=True)
    date_of_birth           = Column(DateTime(timezone=False), nullable=True)
    country_of_residence    = Column(String(100), nullable=True)
    timezone                = Column(String(50), default="UTC", nullable=False)

    # back-ref from FeedItem
    feed_items              = relationship("FeedItem", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
