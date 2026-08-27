from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any
import pandas as pd

from app.api import deps
from app.models.core_models import Inventory, Warehouse, DemandRecord
from app.schemas.shortage import ShortagePredictRequest, ShortagePredictionResponse
from app.intelligence.shortage.predictor import shortage_predictor
from app.intelligence.forecasting.lstm import lstm_forecaster

router = APIRouter()

def prepare_data(demand_records) -> pd.DataFrame:
    data = []
    for r in demand_records:
        data.append({
            "date": r.timestamp.date(),
            "quantity": float(r.quantity)
        })
    df = pd.DataFrame(data)
    df = df.groupby("date")["quantity"].sum().reset_index()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values("date")
    
    # Fill missing dates with 0
    if len(df) > 0:
        idx = pd.date_range(df['date'].min(), df['date'].max())
        df = df.set_index('date').reindex(idx, fill_value=0.0).rename_axis('date').reset_index()
    return df

@router.post("/predict", response_model=ShortagePredictionResponse)
def predict_shortage(
    request: ShortagePredictRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Calculate stockout ETA and shortage probability.
    """
    # 1. Calculate Current Stock
    total_stock_result = db.query(func.sum(Inventory.quantity)).join(Warehouse).filter(
        Warehouse.location_id == request.location_id,
        Inventory.resource_id == request.resource_id
    ).scalar()
    
    current_stock = float(total_stock_result) if total_stock_result else 0.0

    # 2. Get Forecasts
    demand_records = db.query(DemandRecord).filter(
        DemandRecord.location_id == request.location_id,
        DemandRecord.resource_id == request.resource_id
    ).order_by(DemandRecord.timestamp.asc()).all()

    if not demand_records:
        raise HTTPException(status_code=400, detail="Not enough historical demand data to generate a forecast for shortage prediction.")

    df = prepare_data(demand_records)
    
    predictions = lstm_forecaster.predict(df, request.horizon_days)

    if not predictions:
        raise HTTPException(status_code=400, detail="Failed to generate predictions.")

    daily_demands = [p["predicted_demand"] for p in predictions]

    # 3. Calculate Shortage metrics
    result = shortage_predictor.calculate_shortage(current_stock, daily_demands)

    return ShortagePredictionResponse(
        location_id=request.location_id,
        resource_id=request.resource_id,
        current_stock=result["current_stock"],
        predicted_demand=result["predicted_demand"],
        projected_shortage=result["projected_shortage"],
        days_until_stockout=result["days_until_stockout"],
        shortage_probability=result["shortage_probability"],
        status=result["status"]
    )
