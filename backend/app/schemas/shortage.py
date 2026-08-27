from pydantic import BaseModel
from typing import Optional

class ShortagePredictRequest(BaseModel):
    location_id: int
    resource_id: int
    horizon_days: int = 7
    forecast_model_type: str = "xgboost"

class ShortagePredictionResponse(BaseModel):
    location_id: int
    resource_id: int
    current_stock: float
    predicted_demand: float
    projected_shortage: float
    days_until_stockout: Optional[float]
    shortage_probability: float
    status: str  # SAFE, WATCH, WARNING, CRITICAL
