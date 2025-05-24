from sqlalchemy import (
    Column, Integer, String, DateTime, Text, JSON, Enum, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class FeedType(str, enum.Enum):
    NEWS      = "news"
    ANNOUNCE  = "announce"
    TWEET     = "tweet"

class FeedItem(Base):
    __tablename__ = "feed_items"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    type        = Column(Enum(FeedType), nullable=False)
    source      = Column(String(100), nullable=False)   # ex. "reuters", "twitter"
    original_id = Column(String(200), nullable=False)   # external ID
    content     = Column(Text, nullable=False)
    meta = Column("metadata", JSON, default={})
    fetched_at  = Column(DateTime(timezone=False), server_default=func.now())
    summary     = Column(Text, nullable=True)

    user        = relationship("User", back_populates="feed_items")
