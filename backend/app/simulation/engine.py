from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.models.core_models import Crisis, Location, Resource, Route, Inventory, DemandRecord, Warehouse
from app.simulation.scenarios import SCENARIOS

def seed_base_data_if_empty(db: Session):
    """Seed basic locations, resources, routes, and historical time-series if empty."""
    if db.query(Location).count() == 0:
        zones = [
            Location(name="Zone A (North Hospital Depot)", latitude=13.118, longitude=80.220, population=180000, vulnerability_score=0.75, accessibility_score=0.80),
            Location(name="Zone B (Central Logistics Base)", latitude=13.050, longitude=80.245, population=250000, vulnerability_score=0.50, accessibility_score=0.95),
            Location(name="Zone C (South Coastal Relief)", latitude=12.970, longitude=80.215, population=210000, vulnerability_score=0.85, accessibility_score=0.60),
            Location(name="Zone D (West Medical Center)", latitude=13.040, longitude=80.140, population=160000, vulnerability_score=0.60, accessibility_score=0.85),
            Location(name="Zone E (East Harbor Shelter)", latitude=13.090, longitude=80.290, population=190000, vulnerability_score=0.70, accessibility_score=0.75),
        ]
        db.add_all(zones)
        db.commit()

    if db.query(Resource).count() == 0:
        resources = [
            Resource(name="Insulin", category="Medical", unit="vials", criticality="HIGH", shelf_life=30),
            Resource(name="First Aid Kits", category="Medical", unit="kits", criticality="HIGH", shelf_life=365),
            Resource(name="Rice Packs", category="Food", unit="kg", criticality="MEDIUM", shelf_life=180),
            Resource(name="Drinking Water", category="Water", unit="liters", criticality="HIGH", shelf_life=90),
        ]
        db.add_all(resources)
        db.commit()

    if db.query(Route).count() == 0:
        routes = [
            Route(source_location=1, destination_location=2, distance=14.2, estimated_time=28.0, status="OPEN", risk_score=0.15),
            Route(source_location=2, destination_location=3, distance=18.5, estimated_time=36.0, status="OPEN", risk_score=0.25),
            Route(source_location=1, destination_location=3, distance=28.0, estimated_time=55.0, status="OPEN", risk_score=0.20),
            Route(source_location=2, destination_location=4, distance=12.0, estimated_time=22.0, status="OPEN", risk_score=0.10),
            Route(source_location=1, destination_location=4, distance=16.8, estimated_time=32.0, status="OPEN", risk_score=0.15),
            Route(source_location=2, destination_location=5, distance=11.5, estimated_time=24.0, status="OPEN", risk_score=0.10),
            Route(source_location=3, destination_location=5, distance=21.0, estimated_time=42.0, status="OPEN", risk_score=0.30),
            Route(source_location=4, destination_location=3, distance=19.5, estimated_time=38.0, status="OPEN", risk_score=0.18),
        ]
        db.add_all(routes)
        db.commit()
        
    if db.query(Warehouse).count() == 0:
        warehouses = [
            Warehouse(name="Central Strategic Depot", location_id=2, capacity=150000.0, operational_status="ONLINE"),
            Warehouse(name="North Regional Stockpile", location_id=1, capacity=75000.0, operational_status="ONLINE"),
            Warehouse(name="South Coastal Facility", location_id=3, capacity=60000.0, operational_status="ONLINE"),
            Warehouse(name="West Reserve Hub", location_id=4, capacity=50000.0, operational_status="ONLINE")
        ]
        db.add_all(warehouses)
        db.commit()

    if db.query(Inventory).count() == 0:
        inventories = []
        for w_id in range(1, 5):  # 4 warehouses
            for r_id in range(1, 5):  # 4 resources
                base_qty = 6000.0 if w_id == 1 else 3000.0
                inventories.append(Inventory(warehouse_id=w_id, resource_id=r_id, quantity=base_qty, reserved_quantity=0.0, minimum_threshold=1000.0))
        db.add_all(inventories)
        db.commit()

    # Seed 14 days of realistic historical demand if empty for ML training
    if db.query(DemandRecord).count() == 0:
        historical_demands = []
        base_time = datetime.utcnow() - timedelta(days=14)
        for day in range(14):
            day_time = base_time + timedelta(days=day)
            for loc_id in range(1, 6):
                for res_id in range(1, 5):
                    # Slight upward trend with weekday variation
                    qty = 200 + (day * 15) + random.uniform(20, 80)
                    historical_demands.append(DemandRecord(
                        location_id=loc_id,
                        resource_id=res_id,
                        timestamp=day_time,
                        quantity=round(qty, 1),
                        source="HISTORICAL_TELEMETRY"
                    ))
        db.add_all(historical_demands)
        db.commit()


def start_simulation(db: Session, scenario_name: str, affected_zones: list[int], population_affected: int, duration_days: int) -> Crisis:
    seed_base_data_if_empty(db)
    
    scenario = SCENARIOS.get(scenario_name)
    if not scenario:
        raise ValueError(f"Scenario {scenario_name} not found")

    # Create Crisis Record
    crisis = Crisis(
        name=f"Simulated {scenario['type']} - {datetime.utcnow().strftime('%Y%m%d')}",
        type=scenario['type'],
        severity=scenario['severity'],
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(days=duration_days),
        affected_population=population_affected,
        status="ACTIVE"
    )
    db.add(crisis)
    db.commit()
    db.refresh(crisis)

    # Spike Demand based on Multipliers
    resources = db.query(Resource).all()
    locations = db.query(Location).filter(Location.id.in_(affected_zones)).all()
    
    # If no valid locations passed, use all
    if not locations:
        locations = db.query(Location).all()

    for loc in locations:
        for res in resources:
            base_demand = random.uniform(100, 500)
            multiplier = scenario["multipliers"].get(res.category, 1.0)
            spiked_quantity = base_demand * multiplier
            
            demand_record = DemandRecord(
                location_id=loc.id,
                resource_id=res.id,
                timestamp=datetime.utcnow(),
                quantity=spiked_quantity,
                source="SIMULATION_ENGINE"
            )
            db.add(demand_record)
            
    # Simulate Road Closures
    routes = db.query(Route).all()
    for route in routes:
        route.status = "OPEN"
        route.risk_score = 0.1
        
    for route in routes:
        if random.random() < scenario["road_closure_probability"]:
            route.status = "CLOSED"
            route.risk_score = 1.0
            route.risk_score = 1.0
            
    db.commit()
    return crisis

def trigger_event(db: Session, event_type: str, payload: dict) -> dict:
    if event_type == "ROAD_CLOSURE":
        route_id = payload.get("route_id")
        route = db.query(Route).filter(Route.id == route_id).first()
        if route:
            route.status = "CLOSED"
            route.risk_score = 1.0
            db.commit()
            return {"status": "success", "message": f"Route {route_id} closed"}
        return {"status": "error", "message": "Route not found"}
        
    elif event_type == "DEMAND_SPIKE":
        location_id = payload.get("location_id")
        resource_id = payload.get("resource_id")
        increase_pct = payload.get("increase_pct", 0.5) # default 50% increase
        
        # Add new demand record
        new_demand = DemandRecord(
            location_id=location_id,
            resource_id=resource_id,
            timestamp=datetime.utcnow(),
            quantity=1000 * (1 + increase_pct), # simplified
            source="SIMULATION_SPIKE"
        )
        db.add(new_demand)
        db.commit()
        return {"status": "success", "message": f"Demand spiked for resource {resource_id} at location {location_id}"}
    
    return {"status": "error", "message": "Unknown event type"}
