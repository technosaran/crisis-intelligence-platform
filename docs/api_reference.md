# API Reference

*Note: View the interactive Swagger documentation at `http://localhost:8000/docs` while the server is running.*

### Simulation
- `POST /api/v1/simulation/run`: Triggers a simulated crisis, generating fake locations, resources, and sudden demand spikes.

### Demand & Inventory
- `GET /api/v1/inventory/{location_id}`: Retrieves current stock levels.
- `GET /api/v1/demand/{location_id}`: Retrieves historical consumption data.

### Intelligence & Forecasting
- `POST /api/v1/forecast/predict`: Generates 7-14 day demand predictions using Baseline, XGBoost, or LSTM models.
- `POST /api/v1/shortage/predict`: Calculates stockout ETA and probability.
- `GET /api/v1/priority/rank/{crisis_id}/{resource_id}`: Returns normalized priority rankings for all zones.

### Natural Language Processing
- `POST /api/v1/nlp/analyze`: Ingests raw text, extracts location/resource/urgency, and saves a `CrisisSignal`.

### Optimization
- `POST /api/v1/allocation/optimize`: Distributes limited supply mathematically using Linear Programming.
- `POST /api/v1/routing/calculate`: Generates Dijkstra/A* paths.
- `POST /api/v1/routing/reroute`: Recalculates paths avoiding dynamically blocked edges.

### Automation & Decision
- `POST /api/v1/decision/evaluate`: Processes all state data to output a final directive (`ALLOCATE`, `DISPATCH`, `REPLENISH`).
- `GET /api/v1/alerts`: Retrieves the feed of autonomous system alerts.
- `POST /api/v1/alerts/run_cycle`: Manually triggers the Python background scanner.
