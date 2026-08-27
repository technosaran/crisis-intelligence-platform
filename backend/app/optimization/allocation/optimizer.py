import math
from ortools.linear_solver import pywraplp
from typing import List, Dict, Any

class ResourceAllocationOptimizer:
    def __init__(self):
        pass

    def optimize_allocation(
        self, 
        total_supply: float, 
        demands: List[Dict],
        fairness_ratio: float = 0.0
    ) -> Dict[str, Any]:
        """
        Single-pool linear programming resource allocation with optional minimum fairness guarantee.
        demands format: [{'location_id': 1, 'location_name': 'A', 'demand': 7000, 'priority_score': 95.0}, ...]
        """
        solver = pywraplp.Solver.CreateSolver('GLOP')
        if not solver:
            return {"status": "error", "error": "GLOP solver not available."}

        total_demand = sum(loc.get("demand", 0.0) for loc in demands)
        if total_demand <= 0:
            return {
                "status": "success",
                "total_allocated": 0.0,
                "total_unmet_demand": 0.0,
                "allocations": []
            }

        # 1. Variables
        allocation_vars = {}
        for idx, loc in enumerate(demands):
            d_val = float(loc.get("demand", 0.0))
            # If fairness ratio is set, enforce a minimum allocation bound if total supply allows
            min_alloc = 0.0
            if fairness_ratio > 0 and total_supply > 0:
                # Guaranteed proportion up to fair share
                target_min = d_val * min(fairness_ratio, 0.5)
                if target_min * len(demands) <= total_supply:
                    min_alloc = min(d_val, target_min)
                    
            allocation_vars[idx] = solver.NumVar(min_alloc, d_val, f"alloc_{idx}")

        # 2. Total Supply Constraint
        total_allocated_constraint = solver.Constraint(0, float(total_supply), "total_supply")
        for idx in range(len(demands)):
            total_allocated_constraint.SetCoefficient(allocation_vars[idx], 1.0)

        # 3. Objective Function: Maximize sum of (allocation_i * priority_score_i)
        objective = solver.Objective()
        for idx, loc in enumerate(demands):
            p_score = max(1.0, float(loc.get("priority_score", 10.0)))
            objective.SetCoefficient(allocation_vars[idx], p_score)
        
        objective.SetMaximization()

        # 4. Solve
        status = solver.Solve()

        if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            total_allocated = 0.0
            allocations = []
            
            for idx, loc in enumerate(demands):
                d_val = float(loc.get("demand", 0.0))
                allocated_val = round(allocation_vars[idx].solution_value(), 2)
                total_allocated += allocated_val
                unmet = max(0.0, round(d_val - allocated_val, 2))
                
                perc = round((allocated_val / d_val) * 100, 2) if d_val > 0 else 100.0
                    
                allocations.append({
                    "location_id": loc["location_id"],
                    "location_name": loc["location_name"],
                    "priority_score": loc.get("priority_score", 50.0),
                    "allocated_amount": allocated_val,
                    "unmet_demand": unmet,
                    "fulfilled_percentage": perc
                })
                
            allocations.sort(key=lambda x: x["priority_score"], reverse=True)
            
            return {
                "status": "success",
                "total_allocated": round(total_allocated, 2),
                "total_unmet_demand": round(max(0.0, total_demand - total_allocated), 2),
                "fairness_ratio_applied": fairness_ratio,
                "allocations": allocations
            }
        else:
            return {"status": "error", "error": "Linear programming problem is infeasible under current constraints."}

    def optimize_multi_warehouse_allocation(
        self,
        warehouses: List[Dict], # [{'id': 1, 'name': 'Base A', 'stock': 15000, 'lat': 13.05, 'lng': 80.24}, ...]
        demands: List[Dict],    # [{'location_id': 1, 'location_name': 'Zone A', 'demand': 5000, 'priority_score': 90.0, 'lat': 13.11, 'lng': 80.22}, ...]
        fairness_ratio: float = 0.15
    ) -> Dict[str, Any]:
        """
        Multi-Warehouse to Multi-Zone Transportation LP Optimizer.
        Minimizes transit distance penalties while maximizing high-priority relief delivery.
        """
        solver = pywraplp.Solver.CreateSolver('GLOP')
        if not solver:
            return {"status": "error", "error": "GLOP solver not available."}

        num_w = len(warehouses)
        num_z = len(demands)
        total_supply = sum(w.get("stock", 0.0) for w in warehouses)
        total_demand = sum(z.get("demand", 0.0) for z in demands)

        if num_w == 0 or num_z == 0:
            return {"status": "error", "error": "Warehouses and demands must not be empty."}

        # 1. Variables: ship_var[w_idx, z_idx] = quantity shipped from warehouse w to zone z
        ship_vars = {}
        for w_idx, wh in enumerate(warehouses):
            w_cap = float(wh.get("stock", 0.0))
            for z_idx, z in enumerate(demands):
                z_dem = float(z.get("demand", 0.0))
                ship_vars[(w_idx, z_idx)] = solver.NumVar(0.0, min(w_cap, z_dem), f"ship_{w_idx}_{z_idx}")

        # 2. Constraints
        # Warehouse capacity constraints: sum_z ship(w, z) <= stock(w)
        for w_idx, wh in enumerate(warehouses):
            w_constraint = solver.Constraint(0.0, float(wh.get("stock", 0.0)), f"wh_cap_{w_idx}")
            for z_idx in range(num_z):
                w_constraint.SetCoefficient(ship_vars[(w_idx, z_idx)], 1.0)

        # Zone demand constraints: sum_w ship(w, z) <= demand(z)
        # With minimum fairness guarantee
        for z_idx, z in enumerate(demands):
            z_dem = float(z.get("demand", 0.0))
            min_guarantee = 0.0
            if fairness_ratio > 0 and total_supply > 0:
                min_guarantee = min(z_dem, z_dem * fairness_ratio)
                if min_guarantee * num_z > total_supply:
                    min_guarantee = 0.0
                    
            z_constraint = solver.Constraint(min_guarantee, z_dem, f"zone_dem_{z_idx}")
            for w_idx in range(num_w):
                z_constraint.SetCoefficient(ship_vars[(w_idx, z_idx)], 1.0)

        # 3. Objective Function
        # Maximize: sum_w_z [ Priority_z * 10 - Distance(w, z) * 0.02 ] * ship(w, z)
        objective = solver.Objective()
        for w_idx, wh in enumerate(warehouses):
            w_lat, w_lng = wh.get("lat", 13.05), wh.get("lng", 80.24)
            for z_idx, z in enumerate(demands):
                z_lat, z_lng = z.get("lat", 13.05), z.get("lng", 80.24)
                
                # Approximate Euclidean distance in km
                dist_km = math.sqrt((w_lat - z_lat)**2 + (w_lng - z_lng)**2) * 111.0
                priority_weight = float(z.get("priority_score", 50.0))
                
                coef = (priority_weight * 5.0) - (dist_km * 0.1)
                objective.SetCoefficient(ship_vars[(w_idx, z_idx)], max(0.1, coef))

        objective.SetMaximization()
        status = solver.Solve()

        if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            shipping_matrix = []
            zone_totals = {z_idx: 0.0 for z_idx in range(num_z)}
            warehouse_totals = {w_idx: 0.0 for w_idx in range(num_w)}
            total_shipped = 0.0

            for w_idx, wh in enumerate(warehouses):
                w_lat, w_lng = wh.get("lat", 13.05), wh.get("lng", 80.24)
                for z_idx, z in enumerate(demands):
                    qty = round(ship_vars[(w_idx, z_idx)].solution_value(), 2)
                    if qty > 0:
                        total_shipped += qty
                        zone_totals[z_idx] += qty
                        warehouse_totals[w_idx] += qty
                        z_lat, z_lng = z.get("lat", 13.05), z.get("lng", 80.24)
                        dist_km = round(math.sqrt((w_lat - z_lat)**2 + (w_lng - z_lng)**2) * 111.0, 1)

                        shipping_matrix.append({
                            "warehouse_id": wh.get("id"),
                            "warehouse_name": wh.get("name"),
                            "location_id": z.get("location_id"),
                            "location_name": z.get("location_name"),
                            "shipped_amount": qty,
                            "distance_km": dist_km
                        })

            # Zone breakdown
            allocations = []
            for z_idx, z in enumerate(demands):
                d_val = float(z.get("demand", 0.0))
                alloc_val = round(zone_totals[z_idx], 2)
                unmet = max(0.0, round(d_val - alloc_val, 2))
                perc = round((alloc_val / d_val) * 100, 1) if d_val > 0 else 100.0

                allocations.append({
                    "location_id": z.get("location_id"),
                    "location_name": z.get("location_name"),
                    "priority_score": z.get("priority_score", 50.0),
                    "requested_demand": d_val,
                    "allocated_amount": alloc_val,
                    "unmet_demand": unmet,
                    "fulfilled_percentage": perc
                })

            allocations.sort(key=lambda x: x["priority_score"], reverse=True)

            return {
                "status": "success",
                "total_supply": total_supply,
                "total_demand": total_demand,
                "total_allocated": round(total_shipped, 2),
                "total_unmet_demand": round(max(0.0, total_demand - total_shipped), 2),
                "fairness_ratio": fairness_ratio,
                "allocations": allocations,
                "shipping_matrix": shipping_matrix
            }
        else:
            return {"status": "error", "error": "Multi-warehouse LP is infeasible."}

allocation_optimizer = ResourceAllocationOptimizer()

