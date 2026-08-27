from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any
from pydantic import BaseModel
from typing import Dict, Optional

from app.api import deps
from app.models.core_models import Location, Route, CrisisSignal, CrisisReport, DemandForecast, Inventory
from app.schemas.priority import PriorityRankingResponse, LocationPriority
from app.intelligence.scoring.priority import priority_engine
from app.intelligence.shortage.predictor import shortage_predictor

router = APIRouter()

@router.get("/rank/{crisis_id}/{resource_id}", response_model=PriorityRankingResponse)
def get_priority_rankings(
    crisis_id: int,
    resource_id: int,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Generate priority rankings for all locations based on multi-factor risks.
    """
    locations = db.query(Location).all()
    if not locations:
        raise HTTPException(status_code=404, detail="No locations found")

    locations_data = []

    for loc in locations:
        # 1. Base Info
        data = {
            "location_id": loc.id,
            "location_name": loc.name,
            "population": loc.population,
            "vulnerability_score": loc.vulnerability_score,
            "accessibility_risk": 1.0 - loc.accessibility_score # rough proxy
        }

        # 2. Medical Urgency from NLP Signals
        # Find the most severe recent signal for this location
        signal = db.query(CrisisSignal).filter(
            func.lower(CrisisSignal.location) == loc.name.lower()
        ).order_by(CrisisSignal.id.desc()).first()
        
        data["medical_urgency_raw"] = signal.urgency if signal else "WATCH"

        # 3. Accessibility Risk from Routes
        # Check if incoming routes are closed
        closed_routes = db.query(Route).filter(
            Route.destination_location == loc.id,
            Route.status == "CLOSED"
        ).count()
        if closed_routes > 0:
            data["accessibility_risk"] = 1.0

        # 4. Shortage Probability — calculated using shortage_predictor
        # Calculate for specific resource
        forecasts = db.query(DemandForecast).filter(
            DemandForecast.location_id == loc.id,
            DemandForecast.resource_id == resource_id
        ).order_by(DemandForecast.forecast_timestamp.asc()).limit(7).all()
        
        daily_demands = [f.predicted_demand for f in forecasts] if forecasts else [0.0]
        
        # Get total stock for the resource
        total_stock = db.query(func.sum(Inventory.quantity)).filter(Inventory.resource_id == resource_id).scalar() or 0.0
        
        shortage_res = shortage_predictor.calculate_shortage(float(total_stock), daily_demands)
        data["shortage_probability"] = shortage_res["shortage_probability"]
        
        locations_data.append(data)

    # Calculate priority rankings and return
    rankings = priority_engine.calculate_priority_rankings(locations_data)

    return PriorityRankingResponse(
        crisis_id=crisis_id,
        resource_id=resource_id,
        rankings=rankings
    )

class CustomWeightsRequest(BaseModel):
    medical_urgency: float = 0.30
    shortage_probability: float = 0.25
    vulnerability: float = 0.20
    population: float = 0.15
    accessibility_risk: float = 0.10

@router.post("/evaluate-weights")
def evaluate_custom_weights(
    request: CustomWeightsRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Recalculates multi-criteria priority rankings across all zones under user-defined AHP weights.
    """
    locations = db.query(Location).all()
    if not locations:
        raise HTTPException(status_code=404, detail="No locations found")

    locations_data = []
    for loc in locations:
        signal = db.query(CrisisSignal).filter(
            func.lower(CrisisSignal.location) == loc.name.lower()
        ).order_by(CrisisSignal.id.desc()).first()

        locations_data.append({
            "location_id": loc.id,
            "location_name": loc.name,
            "population": loc.population,
            "vulnerability_score": loc.vulnerability_score,
            "accessibility_risk": 1.0 - loc.accessibility_score,
            "medical_urgency_raw": signal.urgency if signal else "WARNING",
            "shortage_probability": 0.85 if loc.vulnerability_score > 0.6 else 0.40
        })

    weights_dict = {
        "medical_urgency": request.medical_urgency,
        "shortage_probability": request.shortage_probability,
        "vulnerability": request.vulnerability,
        "population": request.population,
        "accessibility_risk": request.accessibility_risk
    }

    rankings = priority_engine.calculate_priority_rankings(locations_data, custom_weights=weights_dict)

    return {
        "status": "success",
        "applied_weights": weights_dict,
        "rankings": rankings
    }

