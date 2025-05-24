# app/services/__init__.py

"""
Service package initializer: provides singleton instances and functions.
Imports are wrapped to allow tests to run without optional dependencies.
"""

# Financial data service
from .financial_data_service import financial_data_service as FinancialDataService

# LLM provider service
try:
    from .llm_provider_service import llm_service
except ImportError:
    llm_service = None

# Portfolio value computation
try:
    from .portfolio_service import compute_portfolio_value
except ImportError:
    compute_portfolio_value = None

# P&L computation service
try:
    from .portfolio_pnl_service import compute_pnl
except ImportError:
    compute_pnl = None

# Price prediction service
try:
    from .prediction_service import prediction_service
except ImportError:
    prediction_service = None

# Feed fetching service
try:
    from .feed_service import FeedFetcher
except ImportError:
    FeedFetcher = None

# Market trending service
try:
    from .market_service import MarketService
except ImportError:
    MarketService = None

# Web search service (optional Tavily client)
try:
    from .web_search_service import web_search_service as WebSearchService
except ImportError:
    WebSearchService = None
