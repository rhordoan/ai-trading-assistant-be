# app/schemas/transaction.py

from datetime import date as dt_date, datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, condecimal, conint

from app.models.transaction import TransactionType

class TransactionBase(BaseModel):
    symbol: str
    type: TransactionType
    quantity: conint(gt=0)
    price: condecimal(gt=0)

class TransactionCreate(TransactionBase):
    date: dt_date = Field(default_factory=dt_date.today)

class TransactionUpdate(BaseModel):
    symbol: Optional[str] = None
    type: Optional[TransactionType] = None
    quantity: Optional[conint(gt=0)] = None
    price: Optional[condecimal(gt=0)] = None
    date: Optional[dt_date] = None

    class Config:
        orm_mode = True

class Transaction(TransactionBase):
    id: int
    portfolio_id: int
    date: dt_date
    timestamp: datetime

    class Config:
        orm_mode = True
        # <-- this is the new bit:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
