from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from datetime import datetime
from app.services.prediction_service import prediction_service
from app.schemas.prediction import ForecastPoint
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/forecast", tags=["Forecast"])

@router.get(
    "/{symbol}",
    response_model=List[ForecastPoint],
    summary="Forecast next N business days for a symbol"
)
async def get_forecast(
    symbol: str,
    periods: int = Query(10, gt=0, le=30),
    current_user = Depends(get_current_user)
):
    """
    Returnează predicții pe următoarele `periods` zile lucrătoare pentru simbolul dat.
    """
    try:
        data = await prediction_service.forecast(symbol, periods=periods)
        return data
    except Exception as e:
        raise HTTPException(503, f"Forecast error: {str(e)}")
