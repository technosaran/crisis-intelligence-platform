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

def test_convoy_tour():
    """Test multi-stop convoy tour optimizer (TSP heuristic)."""
    locs = [
        MockLocation(1, "Warehouse", 13.0, 80.0),
        MockLocation(2, "Hospital A", 13.1, 80.1),
        MockLocation(3, "Hospital B", 13.2, 80.2),
        MockLocation(4, "Shelter C", 13.15, 80.05)
    ]
    routes = [
        MockRoute(1, 2, 10.0, 15.0),
        MockRoute(2, 3, 10.0, 15.0),
        MockRoute(1, 3, 30.0, 45.0),
        MockRoute(1, 4, 8.0, 12.0),
        MockRoute(4, 2, 7.0, 10.0),
        MockRoute(4, 3, 15.0, 22.0)
    ]
    routing_engine.build_graph(locs, routes)
    
    result = routing_engine.calculate_convoy_tour(origin=1, stop_ids=[2, 3, 4])
    assert result["status"] == "success"
    # Should visit all stops
    assert 2 in result["path"]
    assert 3 in result["path"]
    assert 4 in result["path"]
    # Should start at origin
    assert result["path"][0] == 1

def test_no_path_exists():
    """Test that routing returns error when no path exists."""
    locs = [
        MockLocation(1, "Warehouse", 13.0, 80.0),
        MockLocation(2, "Isolated", 14.0, 81.0)
    ]
    routes = []  # No edges
    routing_engine.build_graph(locs, routes)
    
    res = routing_engine.calculate_dijkstra(1, 2)
    assert res["status"] == "error"

