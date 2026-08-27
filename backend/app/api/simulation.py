from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any
import httpx

from app.api import deps
from app.schemas.simulation import SimulationStartRequest, SimulationEventRequest, SimulationResponse
from app.simulation import engine

router = APIRouter()

@router.post("/start", response_model=SimulationResponse)
def start_simulation(
    request: SimulationStartRequest,
    db: Session = Depends(deps.get_db),
    # Uncomment next line to require admin auth in production:
    # current_user = Depends(deps.get_current_active_admin)
) -> Any:
    """
    Start a new crisis simulation scenario.
    """
    try:
        crisis = engine.start_simulation(
            db=db,
            scenario_name=request.scenario_name,
            affected_zones=request.affected_zones,
            population_affected=request.population_affected,
            duration_days=request.duration_days
        )
        return SimulationResponse(
            status="success",
            message=f"Simulation '{crisis.name}' started successfully.",
            crisis_id=crisis.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.post("/fetch-live-earthquakes")
async def fetch_live_earthquakes(db: Session = Depends(deps.get_db)) -> Any:
    """
    Fetches real-world earthquake data from the USGS API to showcase Live Mode.
    We use the 'significant_month' feed to ensure there is usually at least one event to show.
    """
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch live USGS data.")
            
    data = response.json()
    features = data.get("features", [])
    
    live_locations = []
    for i, feature in enumerate(features[:5]): # Take top 5
        coords = feature["geometry"]["coordinates"] # [longitude, latitude, depth]
        props = feature["properties"]
        
        live_locations.append({
            "id": 9000 + i, # High ID to avoid colliding with simulation IDs
            "name": props["place"],
            "lat": coords[1],
            "lng": coords[0],
            "type": "crisis",
            "severity": "critical" if props["mag"] > 6.0 else "warning",
            "mag": props["mag"]
        })
        
    return {"status": "success", "live_events": live_locations}

@router.post("/event", response_model=SimulationResponse)
def trigger_simulation_event(
    request: SimulationEventRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Trigger a specific event during an active simulation (e.g., Road Closure).
    """
    try:
        result = engine.trigger_event(
            db=db,
            event_type=request.event_type,
            payload=request.payload
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
            
        return SimulationResponse(
            status="success",
            message=result["message"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event trigger failed: {str(e)}")

from app.models.core_models import Location, Resource, Route, Warehouse, Crisis
from app.simulation.scenarios import SCENARIOS

@router.get("/scenarios")
def get_scenarios_catalog():
    """Return catalog of all available crisis scenarios for simulation."""
    return list(SCENARIOS.values())

@router.get("/info")
def get_system_info(db: Session = Depends(deps.get_db)):
    """Fetch base system data for frontend dropdowns."""
    engine.seed_base_data_if_empty(db)
    locations = db.query(Location).all()
    resources = db.query(Resource).all()
    warehouses = db.query(Warehouse).all()
    routes = db.query(Route).all()
    crises = db.query(Crisis).order_by(Crisis.id.desc()).limit(5).all()
    
    return {
        "locations": [
            {
                "id": l.id,
                "name": l.name,
                "lat": l.latitude,
                "lng": l.longitude,
                "population": l.population,
                "vulnerability": l.vulnerability_score
            } for l in locations
        ],
        "resources": [
            {
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "unit": r.unit,
                "criticality": r.criticality
            } for r in resources
        ],
        "warehouses": [
            {
                "id": w.id,
                "name": w.name,
                "location_id": w.location_id,
                "capacity": w.capacity,
                "status": w.operational_status
            } for w in warehouses
        ],
        "routes": [
            {
                "id": rt.id,
                "source": rt.source_location,
                "destination": rt.destination_location,
                "distance": rt.distance,
                "status": rt.status,
                "risk": rt.risk_score
            } for rt in routes
        ],
        "active_crises": [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "severity": c.severity,
                "status": c.status
            } for c in crises
        ]
    }

