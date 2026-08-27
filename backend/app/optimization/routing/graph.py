import networkx as nx
import math
from typing import List, Dict, Any

class RoutingEngine:
    def __init__(self):
        self.G = nx.Graph()
        self.node_positions = {}
        self.node_names = {}

    def build_graph(self, locations: List[Any], routes: List[Any]):
        """
        Builds the NetworkX graph from database Locations and Routes.
        """
        self.G.clear()
        self.node_positions.clear()
        self.node_names.clear()

        # Add Nodes
        for loc in locations:
            self.G.add_node(loc.id, name=loc.name, vulnerability=loc.vulnerability_score)
            self.node_positions[loc.id] = (loc.latitude, loc.longitude)
            self.node_names[loc.id] = loc.name

        # Add Edges
        for route in routes:
            if route.status == "CLOSED":
                continue
                
            dist = float(route.distance)
            time = float(route.estimated_time)
            risk = float(route.risk_score)

            # Safest weight combines distance with risk penalty
            safety_weight = dist * (1.0 + risk * 3.0)
            
            self.G.add_edge(
                route.source_location, 
                route.destination_location, 
                weight=dist,
                time=time,
                risk=risk,
                safety_weight=safety_weight
            )

    def block_edge(self, u: int, v: int):
        """Temporarily removes an edge to simulate a road closure."""
        if self.G.has_edge(u, v):
            attrs = self.G.edges[u, v]
            self.G.remove_edge(u, v)
            return attrs
        return None

    def _euclidean_heuristic(self, u, v, objective="shortest"):
        """Heuristic for A* based on Euclidean distance of lat/lon.
        Scaled appropriately for different objectives to maintain admissibility."""
        pos_u = self.node_positions.get(u)
        pos_v = self.node_positions.get(v)
        if pos_u and pos_v:
            dist_km = math.sqrt((pos_u[0] - pos_v[0])**2 + (pos_u[1] - pos_v[1])**2) * 111.0
            if objective == "fastest":
                # Convert km to minimum possible time (assume max speed ~60 km/h)
                return dist_km * 1.0  # 1 min per km at 60km/h
            elif objective == "safest":
                # Safety weight is dist * (1 + risk*3), minimum risk=0 so minimum weight = dist
                return dist_km
            return dist_km
        return 0

    def _format_route_result(self, path: List[int], algorithm: str) -> Dict:
        dist = 0.0
        time = 0.0
        risk_sum = 0.0
        edge_count = max(1, len(path) - 1)

        waypoints = []
        coordinates = []

        for node_id in path:
            pos = self.node_positions.get(node_id, (0.0, 0.0))
            name = self.node_names.get(node_id, f"Node {node_id}")
            waypoints.append({
                "id": node_id,
                "name": name,
                "lat": pos[0],
                "lng": pos[1]
            })
            coordinates.append([pos[0], pos[1]])

        for u, v in zip(path[:-1], path[1:]):
            if self.G.has_edge(u, v):
                dist += self.G[u][v].get('weight', 0.0)
                time += self.G[u][v].get('time', 0.0)
                risk_sum += self.G[u][v].get('risk', 0.1)

        avg_risk = round(risk_sum / edge_count, 2)

        return {
            "status": "success",
            "path": path,
            "waypoints": waypoints,
            "route_coordinates": coordinates,
            "distance": round(dist, 2),
            "time": round(time, 1),
            "average_risk_score": avg_risk,
            "algorithm": algorithm
        }

    def calculate_dijkstra(self, source: int, destination: int, objective: str = "fastest") -> Dict:
        weight_key = "time" if objective == "fastest" else "safety_weight" if objective == "safest" else "weight"
        try:
            path = nx.dijkstra_path(self.G, source, destination, weight=weight_key)
            return self._format_route_result(path, f"dijkstra ({objective})")
        except nx.NetworkXNoPath:
            return {"status": "error", "message": "No navigable path exists between source and destination."}
        except nx.NodeNotFound:
            return {"status": "error", "message": "Source or destination node not found in spatial graph."}

    def calculate_astar(self, source: int, destination: int, objective: str = "fastest") -> Dict:
        weight_key = "time" if objective == "fastest" else "safety_weight" if objective == "safest" else "weight"
        try:
            path = nx.astar_path(self.G, source, destination, heuristic=lambda u, v: self._euclidean_heuristic(u, v, objective), weight=weight_key)
            return self._format_route_result(path, f"astar ({objective})")
        except nx.NetworkXNoPath:
            return {"status": "error", "message": "No navigable path exists between source and destination."}
        except nx.NodeNotFound:
            return {"status": "error", "message": "Source or destination node not found in spatial graph."}

    def calculate_convoy_tour(self, origin: int, stop_ids: List[int], objective: str = "fastest") -> Dict:
        """
        Multi-Stop Convoy Delivery Tour (TSP / VRP heuristic).
        Given a starting depot and a list of target crisis zones, computes the optimal sequence of stops.
        """
        if not stop_ids:
            return {"status": "error", "message": "No drop-off stops provided."}

        unvisited = [s for s in stop_ids if s != origin]
        if not unvisited:
            return {"status": "error", "message": "At least one destination stop must differ from origin."}

        weight_key = "time" if objective == "fastest" else "safety_weight" if objective == "safest" else "weight"

        current_node = origin
        full_path = [origin]
        ordered_stops = [origin]

        while unvisited:
            best_next = None
            best_dist = float('inf')
            best_subpath = []

            for candidate in unvisited:
                try:
                    p = nx.astar_path(self.G, current_node, candidate, heuristic=lambda u, v: self._euclidean_heuristic(u, v, objective), weight=weight_key)
                    # Calculate path length
                    length = sum(self.G[u][v].get(weight_key, 1.0) for u, v in zip(p[:-1], p[1:]))
                    if length < best_dist:
                        best_dist = length
                        best_next = candidate
                        best_subpath = p
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue

            if best_next is None:
                # If no connected next stop, pop whatever remains
                break

            unvisited.remove(best_next)
            ordered_stops.append(best_next)
            full_path.extend(best_subpath[1:])
            current_node = best_next

        return self._format_route_result(full_path, f"convoy_tour ({objective})")

routing_engine = RoutingEngine()


