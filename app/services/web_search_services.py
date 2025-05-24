from typing import List, Dict, Optional
from app.core.config import settings

# Attempt to import TavilyClient; degrade gracefully if missing
try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

class WebSearchService:
    def __init__(self):
        if TavilyClient is None:
            # Client unavailable; searches will return empty
            self.client = None
            return
        if not settings.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY not set in environment variables.")
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    async def search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Perform a web search and return a list of result dicts.
        Returns empty list if client is unavailable or on error.
        """
        if self.client is None:
            return []
        try:
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Error during Tavily search: {e}")
            return []

    async def get_search_context(
        self,
        query: str,
        max_chars_per_result: int = 1000,
        **kwargs
    ) -> str:
        """
        Fetches search results and assembles a text context.
        Truncates each result's content to max_chars_per_result.
        """
        results = await self.search(query, **kwargs)
        context_parts = []
        for i, result in enumerate(results):
            snippet = result.get("content", "")[:max_chars_per_result]
            url = result.get("url", "N/A")
            context_parts.append(
                f"Source {i+1} (URL: {url}):\n{snippet}\n\n"
            )
        context = "".join(context_parts).strip()
        return context if context else "No relevant information found from web search."

# Singleton instance
web_search_service = WebSearchService()
