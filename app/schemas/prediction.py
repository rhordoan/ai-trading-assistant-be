from pydantic import BaseModel
from datetime import datetime

class ForecastPoint(BaseModel):
    ds: datetime        
    yhat: float         
    
    class Config:
        from_attributes = True
