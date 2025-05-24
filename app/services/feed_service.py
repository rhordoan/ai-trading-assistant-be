import asyncio
from typing import List
from datetime import datetime, timedelta

from app.services.web_search_services import web_search_service
from .llm_provider_service import llm_service
from app.crud.feed import create_feed_item, update_feed_summary
from sqlalchemy.orm import Session

class FeedFetcher:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    async def fetch_news(self, query: str, limit: int = 10):
        # use web_search_service to pull news headlines/text
        results = await web_search_service.search(
            query=query, search_depth="basic", max_results=limit,
            include_domains=["reuters.com", "bloomberg.com"]
        )
        for res in results:
            item = await self._store_item("news", res)
            await self._summarize(item.id, res.get("content", ""))
    
    async def fetch_tweets(self, query: str, limit: int = 10):
        # placeholder: integrate with Twitter API client
        tweets = []  # call your twitter client here
        for t in tweets:
            item = await self._store_item("tweet", {
                "original_id": t["id"],
                "content": t["text"],
                "metadata": {"author": t["user"]}
            })
            await self._summarize(item.id, t["text"])

    async def _store_item(self, typ: str, raw: dict):
        from app.schemas.feed import FeedItemCreate
        dto = FeedItemCreate(
            type=typ,
            source=raw.get("source", "unknown"),
            original_id=raw["original_id"],
            content=raw["content"],
            meta=raw.get("metadata", {})
        )
        return create_feed_item(self.db, self.user_id, dto)

    async def _summarize(self, feed_id: int, text: str):
        prompt = (
            "Summarize the following financial news/tweet in 2 sentences:\n\n"
            + text
        )
        summary = await llm_service.generate_response(prompt)
        update_feed_summary(self.db, feed_id, summary)
