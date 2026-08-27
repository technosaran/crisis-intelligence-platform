from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.models.core_models import Location, Route
from app.schemas.routing import RouteCalculateRequest, RouteCalculateResponse, RouteRerouteRequest, WaypointDetail
from app.optimization.routing.graph import routing_engine

router = APIRouter()

@router.post("/calculate", response_model=RouteCalculateResponse)
def calculate_route(
    request: RouteCalculateRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Calculate optimal route between two points using Dijkstra or A* with customizable optimization objective (fastest, safest, shortest).
    """
    # Fetch Graph Data
    locations = db.query(Location).all()
    routes = db.query(Route).all()
    
    if not locations or not routes:
        raise HTTPException(status_code=400, detail="Graph network data is incomplete.")

    # Build Graph representation
    routing_engine.build_graph(locations, routes)

    objective = request.objective or "fastest"

    # Calculate
    if request.algorithm == "dijkstra":
        result = routing_engine.calculate_dijkstra(request.source_location_id, request.destination_location_id, objective=objective)
    elif request.algorithm == "astar":
        result = routing_engine.calculate_astar(request.source_location_id, request.destination_location_id, objective=objective)
    else:
        raise HTTPException(status_code=400, detail="Unsupported algorithm. Use 'dijkstra' or 'astar'.")

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])

    return RouteCalculateResponse(
        status="success",
        path=result["path"],
        waypoints=[WaypointDetail(**w) for w in result.get("waypoints", [])],
        route_coordinates=result.get("route_coordinates", []),
        total_distance=result["distance"],
        estimated_time_minutes=result["time"],
        average_risk_score=result.get("average_risk_score", 0.1),
        algorithm_used=result["algorithm"]
    )

@router.post("/reroute", response_model=RouteCalculateResponse)
def reroute_dynamic(
    request: RouteRerouteRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Calculate an alternative route after dynamic road closures.
    """
    locations = db.query(Location).all()
    routes = db.query(Route).all()
    
    if not locations or not routes:
        raise HTTPException(status_code=400, detail="Graph network data is incomplete.")

    # Build base graph
    routing_engine.build_graph(locations, routes)

    # Block specified edges
    for edge in request.blocked_edges:
        routing_engine.block_edge(edge.source_id, edge.destination_id)

    objective = request.objective or "fastest"

    # Calculate detour
    if request.algorithm == "dijkstra":
        result = routing_engine.calculate_dijkstra(request.source_location_id, request.destination_location_id, objective=objective)
    elif request.algorithm == "astar":
        result = routing_engine.calculate_astar(request.source_location_id, request.destination_location_id, objective=objective)
    else:
        raise HTTPException(status_code=400, detail="Unsupported algorithm.")

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail="No alternative path exists. Target is completely isolated.")

    return RouteCalculateResponse(
        status="success",
        path=result["path"],
        waypoints=[WaypointDetail(**w) for w in result.get("waypoints", [])],
        route_coordinates=result.get("route_coordinates", []),
        total_distance=result["distance"],
        estimated_time_minutes=result["time"],
        average_risk_score=result.get("average_risk_score", 0.1),
        algorithm_used=result["algorithm"],
        message="Rerouted successfully avoiding blocked roads."
    )

from pydantic import BaseModel
from typing import List, Optional

class ConvoyTourRequest(BaseModel):
    origin_id: int
    stop_ids: List[int]
    objective: Optional[str] = "fastest"

class DispatchRequest(BaseModel):
    route_coordinates: List[List[float]]

from fastapi import BackgroundTasks

@router.post("/dispatch")
def dispatch_convoy(request: DispatchRequest, background_tasks: BackgroundTasks):
    import uuid
    from app.automation.tasks import simulate_truck_gps
    convoy_id = str(uuid.uuid4())[:8]
    background_tasks.add_task(simulate_truck_gps, f"CVY-{convoy_id}", request.route_coordinates)
    return {"status": "dispatched", "convoy_id": f"CVY-{convoy_id}"}

@router.post("/convoy-tour", response_model=RouteCalculateResponse)
def calculate_convoy_tour(
    request: ConvoyTourRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Multi-Stop Convoy Tour Optimizer.
    Calculates the optimal chained delivery route visiting multiple disaster hospital targets.
    """
    locations = db.query(Location).all()
    routes = db.query(Route).all()
    
    if not locations or not routes:
        raise HTTPException(status_code=400, detail="Graph network data is incomplete.")

    routing_engine.build_graph(locations, routes)
    result = routing_engine.calculate_convoy_tour(request.origin_id, request.stop_ids, objective=request.objective or "fastest")

    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message", "Could not solve convoy tour."))

    return RouteCalculateResponse(
        status="success",
        path=result["path"],
        waypoints=[WaypointDetail(**w) for w in result.get("waypoints", [])],
        route_coordinates=result.get("route_coordinates", []),
        total_distance=result["distance"],
        estimated_time_minutes=result["time"],
        average_risk_score=result.get("average_risk_score", 0.1),
        algorithm_used=result["algorithm"],
        message="Optimal Multi-Stop Convoy Tour Computed."
    )



