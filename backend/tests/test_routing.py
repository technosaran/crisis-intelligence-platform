import pytest
from app.optimization.routing.graph import routing_engine

class MockLocation:
    def __init__(self, id, name, lat, lon):
        self.id = id
        self.name = name
        self.latitude = lat
        self.longitude = lon
        self.vulnerability_score = 0.5

class MockRoute:
    def __init__(self, source, dest, dist, time, status="OPEN"):
        self.source_location = source
        self.destination_location = dest
        self.distance = dist
        self.estimated_time = time
        self.status = status
        self.risk_score = 0.1

def test_dijkstra_and_astar():
    locs = [
        MockLocation(1, "Warehouse", 13.0, 80.0),
        MockLocation(2, "Hub", 13.1, 80.1),
        MockLocation(3, "Hospital", 13.2, 80.2)
    ]
    routes = [
        MockRoute(1, 2, 10.0, 15.0),
        MockRoute(2, 3, 10.0, 15.0),
        MockRoute(1, 3, 30.0, 45.0)
    ]
    routing_engine.build_graph(locs, routes)
    
    res_d = routing_engine.calculate_dijkstra(1, 3)
    assert res_d["path"] == [1, 2, 3]
    
def test_dynamic_reroute():
    locs = [
        MockLocation(1, "Warehouse", 13.0, 80.0),
        MockLocation(2, "Hub", 13.1, 80.1),
        MockLocation(3, "Hospital", 13.2, 80.2)
    ]
    routes = [
        MockRoute(1, 2, 10.0, 15.0),
        MockRoute(2, 3, 10.0, 15.0),
        MockRoute(1, 3, 30.0, 45.0)
    ]
    routing_engine.build_graph(locs, routes)
    
    # Normally path is 1->2->3
    # Let's simulate a flood washing away the bridge between 1 and 2
    routing_engine.block_edge(1, 2)
    
    # Recalculate
    res_detour = routing_engine.calculate_astar(1, 3)
    assert res_detour["status"] == "success"
    # Forced to take the direct slower route because hub is blocked
    assert res_detour["path"] == [1, 3]
    assert res_detour["distance"] == 30.0
