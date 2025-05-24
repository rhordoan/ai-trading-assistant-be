# app/services/prediction_service.py

import pandas as pd
from prophet import Prophet
from app.services.financial_data_service import FinancialDataService

class PredictionService:
    def __init__(self):
        self.fd = FinancialDataService()

    async def forecast(self, symbol: str, periods: int = 10):
        """
        Forecast the next `periods` days of stock prices for a given symbol.
        """
        # 1) Fetch daily OHLC data
        ts = await self.fd.get_daily_series(symbol, outputsize="full")
        if not ts:
            raise ValueError(f"No data found for symbol: {symbol}")

        # 2) Convert to DataFrame
        df = (
            pd.DataFrame.from_dict(ts, orient="index")
              .reset_index()
              .rename(columns={"index": "ds", "4. close": "y"})
              [["ds", "y"]]
        )
        df["ds"] = pd.to_datetime(df["ds"])
        df["y"] = df["y"].astype(float)

        # 3) Train Prophet
        model = Prophet(daily_seasonality=True)
        model.fit(df)

        # 4) Make future DataFrame & predict
        future = model.make_future_dataframe(periods=periods, freq="B")
        forecast = model.predict(future)

        # 5) Return only the last `periods` rows
        preds = forecast[["ds", "yhat"]].tail(periods)
        return preds.to_dict("records")

# singleton you import elsewhere
prediction_service = PredictionService()
