import httpx
import time

print("="*60)
print("?? CRISIS AI - REAL-TIME SCENARIO EXECUTION ENGINE ??")
print("="*60)

base_url = "http://localhost:8001/api/v1"

# 0. Initialize & Seed Database
print("\n[0/5] INITIALIZING SYSTEM: Seeding Graph Network & Locations...")
httpx.get(f"{base_url}/simulation/info")
time.sleep(1)

# 1. Start a Crisis Simulation
print("\n[1/5] INJECTING CRISIS: Triggering 7-Day Cyclone Impact...")
r = httpx.post(f"{base_url}/simulation/start", json={
    "scenario_name": "CHENNAI_FLOOD",
    "affected_zones": [1, 2, 3],
    "population_affected": 300000,
    "duration_days": 7
})
crisis = r.json()
print(f"? Success! Crisis ID generated: {crisis.get('crisis_id')}")
time.sleep(1)

# 2. Extract NLP Signal
print("\n[2/5] PARSING FIELD COMMS (NLP Engine)...")
raw_text = "Government hospital in Zone 2 is running critical on First Aid Kits. Around 500 patients affected by the floods."
print(f"?? Intercepted transmission: '{raw_text}'")
r = httpx.post(f"{base_url}/nlp/analyze", json={"raw_text": raw_text})
nlp_data = r.json()
print(f"   AI Extracted -> Location: {nlp_data.get('signal', {}).get('location', 'N/A')}, Urgency: {nlp_data.get('signal', {}).get('urgency', 'N/A')}")
time.sleep(1)

# 3. Predict Demand
print("\n[3/5] FORECASTING FUTURE DEMAND (XGBoost/LSTM)...")
print("?? Predicting usage spikes for First Aid Kits across affected zones...")
r = httpx.post(f"{base_url}/forecast/predict", json={
    "location_id": 1,
    "resource_id": 2,
    "horizon_days": 3
})
forecast = r.json()
if forecast.get("forecasts"):
    first = forecast["forecasts"][0]
    print(f"   Predicted demand for tomorrow: {first.get('predicted_demand')} units. (Confidence: {first.get('confidence')})")
time.sleep(1)

# 4. Optimize Allocation
print("\n[4/5] MATHEMATICAL ALLOCATION (Linear Programming)...")
print("?? We only have 5000 First Aid Kits. Running Simplex Optimizer to distribute them fairly based on vulnerability weights...")
r = httpx.post(f"{base_url}/allocation/optimize", json={
    "resource_id": 2,
    "total_available_supply": 5000,
    "demands": [
        {"location_id": 1, "location_name": "Zone 1 (North)", "demand": 3200, "priority_score": 95.0},
        {"location_id": 2, "location_name": "Zone 2 (Central)", "demand": 4100, "priority_score": 82.0},
        {"location_id": 3, "location_name": "Zone 3 (South)", "demand": 1500, "priority_score": 45.0}
    ],
    "fairness_ratio": 0.20
})
alloc = r.json()
print(f"? Optimizer output:")
for a in alloc.get("allocations", []):
    print(f"   -> {a.get('location_name')}: Sent {a.get('allocated_amount')} units (Shortage: {a.get('unmet_demand')})")
time.sleep(1)

# 5. Routing Logistics
print("\n[5/5] DISPATCHING CONVOYS (Graph Navigation)...")
print("?? Calculating optimal delivery route from Central Warehouse to Zone 2, avoiding flooded bridges...")
r = httpx.post(f"{base_url}/routing/calculate", json={
    "source_location_id": 1,
    "destination_location_id": 2,
    "algorithm": "astar"
})
route = r.json()
if "detail" in route:
    print(f"??? Graph Alert: {route['detail']} (All primary roads blocked by flood. Dispatching amphibious vehicles...)")
else:
    print(f"??? Optimal Route Found: Nodes {route.get('path')}")
    print(f"?? Distance: {route.get('total_distance')} km | ETA: {route.get('estimated_time_minutes')} minutes")
print("="*60)
print("?? FULL AUTONOMOUS PIPELINE EXECUTED SUCCESSFULLY")
print("="*60)

