# app/services/financial_data_service.py

import asyncio
from typing import List, Tuple, Optional
from app.core.config import settings

try:
    from alpha_vantage.timeseries import TimeSeries
except ImportError:
    TimeSeries = None

class FinancialDataService:
    def __init__(self):
        if TimeSeries is None:
            self.ts = None
        else:
            if not settings.ALPHA_VANTAGE_API_KEY:
                raise ValueError("ALPHA_VANTAGE_API_KEY not set in environment variables.")
            self.ts = TimeSeries(key=settings.ALPHA_VANTAGE_API_KEY, output_format='json')

    async def _run_sync(self, func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def get_stock_quote(self, symbol: str) -> dict:
        """
        Fetch latest stock quote for `symbol`. Returns empty dict if unavailable.
        """
        if self.ts is None:
            return {}
        try:
            data, _ = await self._run_sync(self.ts.get_quote_endpoint, symbol)
            return data
        except Exception as e:
            print(f"Error fetching stock quote for {symbol}: {e}")
            return {}

    async def get_daily_series(self, symbol: str, outputsize: str = "compact") -> dict:
        """
        Fetch daily OHLC time series for `symbol`.
        Returns dict of { date: { '1. open':..., '4. close':... } } or empty dict.
        """
        if self.ts is None:
            return {}
        try:
            data, _ = await self._run_sync(self.ts.get_daily, symbol=symbol, outputsize=outputsize)
            return data.get("Time Series (Daily)", {})
        except Exception as e:
            print(f"Error fetching daily series for {symbol}: {e}")
            return {}

# Singleton instance
financial_data_service = FinancialDataService()
