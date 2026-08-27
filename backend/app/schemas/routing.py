from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class WaypointDetail(BaseModel):
    id: int
    name: str
    lat: float
    lng: float

class RouteCalculateRequest(BaseModel):
    source_location_id: int
    destination_location_id: int
    algorithm: str = "astar"  # options: dijkstra, astar
    objective: Optional[str] = "fastest"  # options: fastest, safest, shortest

class RouteCalculateResponse(BaseModel):
    status: str
    path: List[int]
    waypoints: Optional[List[WaypointDetail]] = []
    route_coordinates: Optional[List[List[float]]] = []
    total_distance: float
    estimated_time_minutes: float
    average_risk_score: Optional[float] = 0.1
    algorithm_used: str
    message: Optional[str] = None

class RouteEdge(BaseModel):
    source_id: int
    destination_id: int

class RouteRerouteRequest(BaseModel):
    source_location_id: int
    destination_location_id: int
    blocked_edges: List[RouteEdge]
    algorithm: str = "astar"
    objective: Optional[str] = "fastest"

