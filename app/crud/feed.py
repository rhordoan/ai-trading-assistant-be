from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.feed import FeedItem
from app.schemas.feed import FeedItemCreate, FeedFilters
from sqlalchemy import and_

def create_feed_item(
    db: Session, user_id: int, item: FeedItemCreate
) -> FeedItem:
    fi = FeedItem(user_id=user_id, **item.dict())
    db.add(fi); db.commit(); db.refresh(fi)
    return fi

def list_feed_items(
    db: Session, user_id: int, filters: FeedFilters
) -> List[FeedItem]:
    q = db.query(FeedItem).filter(FeedItem.user_id == user_id)
    if filters.types:
        q = q.filter(FeedItem.type.in_(filters.types))
    if filters.sources:
        q = q.filter(FeedItem.source.in_(filters.sources))
    if filters.since:
        q = q.filter(FeedItem.fetched_at >= filters.since)
    if filters.until:
        q = q.filter(FeedItem.fetched_at <= filters.until)
    return q.order_by(FeedItem.fetched_at.desc()) \
            .offset(filters.skip).limit(filters.limit).all()

def update_feed_summary(
    db: Session, feed_id: int, summary: str
) -> Optional[FeedItem]:
    fi = db.query(FeedItem).get(feed_id)
    if not fi:
        return None
    fi.summary = summary
    db.add(fi); db.commit(); db.refresh(fi)
    return fi
