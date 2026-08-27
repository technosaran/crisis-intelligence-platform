from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ForecastRequest(BaseModel):
    location_id: int
    resource_id: int
    horizon_days: int = 7
    model_type: str = "xgboost"  # options: moving_average, linear_regression, xgboost, lstm

class ForecastResponseBase(BaseModel):
    location_id: Optional[int] = None
    resource_id: Optional[int] = None
    forecast_timestamp: datetime
    predicted_demand: float
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    confidence: float
    model_version: str

class ForecastResponse(ForecastResponseBase):
    id: int
    
    model_config = {"from_attributes": True}

class ForecastSeriesResponse(BaseModel):
    status: str
    forecasts: List[ForecastResponseBase]
