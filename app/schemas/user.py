from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.user import TradingExperienceLevel, RiskAppetite, InvestmentGoals

class UserBase(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    profile_picture_url: Optional[str] = None
    is_active: Optional[bool] = True
    trading_experience: Optional[TradingExperienceLevel] = None
    risk_appetite: Optional[RiskAppetite] = None
    investment_goals: Optional[InvestmentGoals] = None
    preferred_asset_classes: Optional[List[str]] = []
    interests_for_feed: Optional[List[str]] = []
    date_of_birth: Optional[datetime] = None
    country_of_residence: Optional[str] = None
    timezone: Optional[str] = "UTC"
    
class UserCreate(UserBase):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    
class UserUpdate(UserBase):
    pass
    
class UserInDBBase(UserBase):
    id: int
    class ConfigDict:
        from_attributes = True
        
class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class UserOut(BaseModel):
    id:        int
    username:  str
    email:     EmailStr
    full_name: Optional[str] = None

    class Config:
        orm_mode = True