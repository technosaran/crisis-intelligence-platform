from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any
import datetime
import pandas as pd
import numpy as np

from app.api import deps
from app.models.core_models import DemandRecord, DemandForecast, Location, Resource
from app.schemas.forecast import ForecastRequest, ForecastSeriesResponse, ForecastResponse
from app.intelligence.forecasting.lstm import lstm_forecaster
from app.intelligence.forecasting.baselines import baseline_forecaster
from app.simulation.engine import seed_base_data_if_empty

router = APIRouter()

def prepare_data(demand_records) -> pd.DataFrame:
    data = []
    for r in demand_records:
        data.append({
            "date": r.timestamp.date(),
            "quantity": float(r.quantity)
        })
    df = pd.DataFrame(data)
    if len(df) > 0:
        df = df.groupby("date")["quantity"].sum().reset_index()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values("date")
        
    # COLD START FIX: Inject Baseline Profile if data is severely lacking
    if len(df) < 5:
        import datetime as dt
        base_date = dt.date.today() - dt.timedelta(days=7)
        # Standard disaster curve profile (transfer learning baseline)
        baseline_profile = [200.0, 800.0, 2500.0, 3100.0, 2900.0, 1500.0, 800.0]
        synthetic_data = []
        for i, val in enumerate(baseline_profile):
            synthetic_data.append({
                "date": base_date + dt.timedelta(days=i),
                "quantity": val
            })
        synth_df = pd.DataFrame(synthetic_data)
        synth_df['date'] = pd.to_datetime(synth_df['date'])
        if len(df) > 0:
            df = pd.concat([synth_df, df]).groupby('date')['quantity'].max().reset_index()
        else:
            df = synth_df
        df = df.sort_values("date")

    # Fill missing dates with 0
    if len(df) > 0:
        idx = pd.date_range(df['date'].min(), df['date'].max())
        df = df.set_index('date').reindex(idx, fill_value=0.0).rename_axis('date').reset_index()
    return df

@router.post("/predict", response_model=ForecastSeriesResponse)
def generate_forecast(
    request: ForecastRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Generate a forecast for a specific location and resource using historical demand.
    """
    seed_base_data_if_empty(db)
    
    # Verify entities
    location = db.query(Location).filter(Location.id == request.location_id).first()
    resource = db.query(Resource).filter(Resource.id == request.resource_id).first()
    
    if not location or not resource:
        raise HTTPException(status_code=404, detail="Location or Resource not found")

    # Fetch historical demand
    demand_records = db.query(DemandRecord).filter(
        DemandRecord.location_id == request.location_id,
        DemandRecord.resource_id == request.resource_id
    ).order_by(DemandRecord.timestamp.asc()).all()

    if not demand_records:
        raise HTTPException(status_code=400, detail="Not enough historical demand data to generate a forecast.")

    df = prepare_data(demand_records)

    # Generate predictions
    model_type = getattr(request, "model_type", "lstm")
    if model_type in ["lstm", None]:
        predictions = lstm_forecaster.predict(df, request.horizon_days)
    elif model_type == "moving_average":
        predictions = baseline_forecaster.moving_average(df, request.horizon_days)
    elif model_type == "linear_regression":
        predictions = baseline_forecaster.linear_regression(df, request.horizon_days)
    elif model_type == "xgboost":
        predictions = baseline_forecaster.xgboost_forecast(df, request.horizon_days)
    else:
        predictions = lstm_forecaster.predict(df, request.horizon_days)

    if not predictions:
         raise HTTPException(status_code=400, detail="Failed to generate predictions due to insufficient data variance.")

    # Save forecasts to DB
    saved_forecasts = []
    for pred in predictions:
        forecast_record = DemandForecast(
            location_id=request.location_id,
            resource_id=request.resource_id,
            forecast_timestamp=pred["forecast_timestamp"],
            predicted_demand=pred["predicted_demand"],
            lower_bound=pred["lower_bound"],
            upper_bound=pred["upper_bound"],
            confidence=pred["confidence"],
            model_version=pred["model_version"]
        )
        db.add(forecast_record)
        saved_forecasts.append(pred)
        
    db.commit()

    for f in saved_forecasts:
        f["location_id"] = request.location_id
        f["resource_id"] = request.resource_id

    return ForecastSeriesResponse(
        status="success",
        forecasts=saved_forecasts
    )

@router.post("/predict-comparison")
def generate_forecast_comparison(
    request: ForecastRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Returns aligned historical actuals alongside LSTM predictions for chart visualization.
    """
    seed_base_data_if_empty(db)
    
    demand_records = db.query(DemandRecord).filter(
        DemandRecord.location_id == request.location_id,
        DemandRecord.resource_id == request.resource_id
    ).order_by(DemandRecord.timestamp.asc()).all()

    if not demand_records:
        raise HTTPException(status_code=400, detail="Insufficient historical demand data.")

    df = prepare_data(demand_records)

    # Historical actuals (latest 7 days)
    chart_series = []
    recent_df = df.tail(7)
    for idx, row in recent_df.iterrows():
        chart_series.append({
            "day": row['date'].strftime("%b %d"),
            "actual": round(float(row['quantity']), 1),
            "lstm": None,
            "xgboost": None,
            "linear_regression": None,
            "moving_average": None,
            "lower_bound": None,
            "upper_bound": None
        })

    # Generate predictions from all 4 models
    h = request.horizon_days
    lstm_preds = lstm_forecaster.predict(df, h)
    ma_preds = baseline_forecaster.moving_average(df, h)
    lr_preds = baseline_forecaster.linear_regression(df, h)
    xgb_preds = baseline_forecaster.xgboost_forecast(df, h)

    for i in range(h):
        pred_date = (df['date'].iloc[-1] + datetime.timedelta(days=i+1)).strftime("%b %d")
        lstm_val = lstm_preds[i]["predicted_demand"] if i < len(lstm_preds) else 0.0
        xgb_val = xgb_preds[i]["predicted_demand"] if i < len(xgb_preds) else 0.0
        lr_val = lr_preds[i]["predicted_demand"] if i < len(lr_preds) else 0.0
        ma_val = ma_preds[i]["predicted_demand"] if i < len(ma_preds) else 0.0
        
        # Use average of available models for confidence band
        avg_val = np.mean([v for v in [lstm_val, xgb_val, lr_val, ma_val] if v > 0]) if any([lstm_val, xgb_val, lr_val, ma_val]) else 0.0

        chart_series.append({
            "day": f"Day +{i+1} ({pred_date})",
            "actual": None,
            "lstm": lstm_val,
            "xgboost": xgb_val,
            "linear_regression": lr_val,
            "moving_average": ma_val,
            "lower_bound": round(float(avg_val) * 0.85, 1),
            "upper_bound": round(float(avg_val) * 1.15, 1)
        })

    # Compute real benchmarks using train/test split
    benchmarks = _compute_benchmarks(df)

    return {
        "location_id": request.location_id,
        "resource_id": request.resource_id,
        "horizon_days": request.horizon_days,
        "chart_data": chart_series,
        "benchmarks": benchmarks
    }


def _compute_benchmarks(df: pd.DataFrame) -> dict:
    """Compute real evaluation metrics using an 80/20 train-test split."""
    if len(df) < 10:
        return {}
    
    split = int(len(df) * 0.8)
    train_df = df.iloc[:split].copy()
    test_df = df.iloc[split:].copy()
    test_actual = test_df['quantity'].values
    horizon = len(test_actual)
    
    results = {}
    
    import logging
    logger = logging.getLogger(__name__)

    # LSTM
    try:
        lstm_preds = lstm_forecaster.predict(train_df, horizon)
        if lstm_preds:
            pred_vals = [p['predicted_demand'] for p in lstm_preds[:len(test_actual)]]
            results['lstm'] = _calc_metrics(test_actual[:len(pred_vals)], pred_vals)
    except Exception as e:
        logger.warning(f"LSTM benchmark failed: {e}")
    
    # XGBoost
    try:
        xgb_preds = baseline_forecaster.xgboost_forecast(train_df, horizon)
        if xgb_preds:
            pred_vals = [p['predicted_demand'] for p in xgb_preds[:len(test_actual)]]
            results['xgboost'] = _calc_metrics(test_actual[:len(pred_vals)], pred_vals)
    except Exception as e:
        logger.warning(f"XGBoost benchmark failed: {e}")
    
    # Linear Regression
    try:
        lr_preds = baseline_forecaster.linear_regression(train_df, horizon)
        if lr_preds:
            pred_vals = [p['predicted_demand'] for p in lr_preds[:len(test_actual)]]
            results['linear_regression'] = _calc_metrics(test_actual[:len(pred_vals)], pred_vals)
    except Exception as e:
        logger.warning(f"Linear Regression benchmark failed: {e}")
    
    # Moving Average
    try:
        ma_preds = baseline_forecaster.moving_average(train_df, horizon)
        if ma_preds:
            pred_vals = [p['predicted_demand'] for p in ma_preds[:len(test_actual)]]
            results['moving_average'] = _calc_metrics(test_actual[:len(pred_vals)], pred_vals)
    except Exception as e:
        logger.warning(f"Moving Average benchmark failed: {e}")
    
    return results


def _calc_metrics(actual: np.ndarray, predicted: list) -> dict:
    """Calculate RMSE, MAE, MAPE, and R² for a set of predictions."""
    actual = np.array(actual, dtype=float)
    predicted = np.array(predicted, dtype=float)
    n = min(len(actual), len(predicted))
    actual = actual[:n]
    predicted = predicted[:n]
    
    if n == 0:
        return {}
    
    rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))
    mae = float(np.mean(np.abs(actual - predicted)))
    
    # MAPE - avoid division by zero
    mask = actual > 0
    mape = float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100) if mask.any() else 0.0
    
    # R²
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    return {
        "rmse": round(rmse, 1),
        "mae": round(mae, 1),
        "mape": round(mape, 1),
        "r2": round(r2, 2)
    }

@router.get("/benchmark")
def get_model_benchmark(
    location_id: int = 1,
    resource_id: int = 1,
    db: Session = Depends(deps.get_db)
) -> Any:
    seed_base_data_if_empty(db)
    demand_records = db.query(DemandRecord).filter(
        DemandRecord.location_id == location_id,
        DemandRecord.resource_id == resource_id
    ).order_by(DemandRecord.timestamp.asc()).all()
    
    if not demand_records:
        return {}
    
    df = prepare_data(demand_records)
    return _compute_benchmarks(df)

@router.get("/", response_model=List[ForecastResponse])
def get_forecasts(
    db: Session = Depends(deps.get_db),
    location_id: int = None,
    resource_id: int = None,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve stored forecasts.
    """
    query = db.query(DemandForecast)
    if location_id:
        query = query.filter(DemandForecast.location_id == location_id)
    if resource_id:
        query = query.filter(DemandForecast.resource_id == resource_id)
        
    return query.order_by(DemandForecast.forecast_timestamp.desc()).offset(skip).limit(limit).all()

