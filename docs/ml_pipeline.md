# Machine Learning & Optimization Pipeline

The core value of this platform resides in its intelligence pipeline, which strictly follows this chronological flow:

## 1. Data Ingestion (Simulation & NLP)
- **Simulation**: Generates structured `DemandRecord` inputs.
- **NLP**: Parses unstructured volunteer reports. Extracts entities (`Location`, `Resource`, `Urgency`) using a mix of dictionary mapping and regex to create `CrisisSignal` objects.

## 2. Demand Forecasting
- **Moving Average & Linear Regression**: Provides a stable baseline.
- **XGBoost**: Trained on historical tabular data, captures feature importance and seasonal drops.
- **PyTorch LSTM**: Processes rolling window chunks of time-series data to predict sudden, explosive spikes that linear models fail to detect. Outputs are saved to `DemandForecast`.

## 3. Shortage Prediction
- **Algorithm**: `days_until_stockout = inventory / daily_demand_forecast`
- Interpolates the exact day stock will run out. Assigns a status (`CRITICAL`, `WARNING`, `SAFE`) and a mathematical probability based on proximity.

## 4. Priority Engine
- **Algorithm**: `Priority = (Medical Urgency * Pop * Shortage Risk * Vulnerability * Accessibility) * 100`
- Normalizes disparate metrics into a strict 0.0-1.0 scale before computing the product.

## 5. Decision Synthesis
- An overarching rule tree determines the operational outcome. If inventory == 0 and shortage is CRITICAL, the engine outputs `REPLENISH`. If inventory > 0 but < demand, it outputs `ALLOCATE`.

## 6. Allocation Optimizer
- Uses **Google OR-Tools** (Linear Programming).
- **Objective**: Maximize `Sum(Allocated * Priority)`.
- **Constraints**: `Sum(Allocated) <= Total Supply`, `Allocated_i <= Demand_i`.
- Ensures mathematical fairness when distributing insufficient medical supplies across multiple high-priority zones.

## 7. Graph Routing
- Represents the road network as a **NetworkX** spatial graph.
- Uses **A* (A-Star)** with a Lat/Lon Euclidean distance heuristic to find optimal routes.
- Supports dynamic rerouting by popping blocked edges mid-flight and recalculating.
