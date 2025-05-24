# app/schemas/feed.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.feed import FeedType

class FeedItemBase(BaseModel):
    type: FeedType
    source: str
    original_id: str
    content: str
    meta: dict = Field(default_factory=dict)

class FeedItemCreate(FeedItemBase):
    """Used when creating a new feed item."""
    pass

class FeedItem(FeedItemBase):
    id: int
    fetched_at: datetime
    summary: Optional[str]

    class Config:
        from_attributes = True

class FeedFilters(BaseModel):
    types: Optional[List[FeedType]] = None
    sources: Optional[List[str]] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    limit: int = Field(50, gt=0, le=200)
    skip: int = Field(0, ge=0)
