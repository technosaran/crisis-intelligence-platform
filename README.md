# AI-Driven Crisis Resource Intelligence & Autonomous Logistics Platform

> **Academic / Final Year Project based on IEEE Standards**

## 📄 Abstract
During natural disasters and large-scale crises, rapid and equitable resource distribution is critical. Traditional crisis management systems rely heavily on manual data entry and reactive decision-making, which often leads to critical stockouts, misallocation of medical supplies, and inefficient routing due to blocked infrastructure. 

This project proposes an **AI-Driven Crisis Resource Intelligence and Autonomous Logistics Platform**. The system leverages Machine Learning (LSTMs, XGBoost) for non-linear demand forecasting, Natural Language Processing (NLP) for real-time field report extraction, Linear Programming (Google OR-Tools) for equitable resource allocation, and Graph-based algorithms (NetworkX) for dynamic route optimization. By automating the intelligence pipeline, the proposed system minimizes human latency and maximizes the impact of available resources in high-priority zones.

**Keywords:** _Crisis Management, Machine Learning, Resource Allocation, NLP, Linear Programming, Shortage Prediction, AI Logistics, IEEE_

---

## 🎯 Problem Statement
- **Delayed Intelligence:** Unstructured field reports from volunteers and victims take too long to parse manually.
- **Reactive Supply Chains:** Resources are only dispatched *after* stockouts occur, leading to critical delays in medical and food supplies.
- **Suboptimal Allocation:** In times of severe scarcity, manual allocation fails to mathematically optimize for severity, vulnerability, and maximum coverage.
- **Static Routing:** Traditional mapping systems fail to account for suddenly impassable terrain or blocked roads during a crisis.

---

## 💡 Proposed System & Base Paper Integration
This project is built to align with standard IEEE research methodologies for intelligent logistics and crisis management. 

> **Base Paper Reference:**  
> *[Insert your IEEE Base Paper Title Here]*  
> *[Insert Authors, Year, and Publication Details Here]*  

**How this project extends the base paper:**
While the base paper may focus on a single aspect (e.g., just routing or just forecasting), this platform provides an **end-to-end autonomous pipeline**:
1. **Intelligent Ingestion:** NLP extracts data from raw text.
2. **Predictive Analytics:** Forecasting models predict *when* a shortage will happen.
3. **Prescriptive Analytics:** Optimization models dictate *how* to distribute limited resources.

---

## 🏗️ System Architecture

The platform follows a decoupled, microservice-ready monorepo architecture:
- **Frontend Layer:** Next.js 14, Tailwind CSS, React-Leaflet for real-time spatial visualization.
- **Backend API Layer:** FastAPI (Python) for high-performance async processing.
- **Intelligence Engine:** PyTorch, scikit-learn, XGBoost for forecasting; spacy for NLP.
- **Optimization Engine:** Google OR-Tools for linear programming; NetworkX for graph routing.
- **Database Layer:** PostgreSQL managed via SQLAlchemy.
- **Orchestration:** Dockerized environment with an optional n8n instance for external webhook alerts (SMS/Slack).

*(See [docs/architecture.md](docs/architecture.md) for more details).*

---

## ⚙️ Core Modules (Methodology)

### 1. NLP Crisis Intelligence (Data Ingestion)
Uses `spacy` and rule-based regex extraction to parse unstructured field reports (e.g., tweets, SMS) into structured `Location`, `Resource`, and `Urgency` signals.

### 2. Demand Forecasting
Predicts non-linear demand spikes using a hybrid approach:
- **Moving Average & Linear Regression:** Provides a stable baseline.
- **XGBoost:** Captures feature importance and seasonal drops.
- **PyTorch LSTM:** Processes time-series data to predict sudden, explosive spikes that linear models fail to detect.

### 3. Shortage Prediction & Priority Engine
Calculates the exact floating-point ETA for stockouts using arithmetic interpolation against live inventory and forecasted demand. The Priority Engine computes a normalized score (0.0 to 1.0) based on Medical Urgency, Population, Vulnerability, and Accessibility.

### 4. Autonomous Decision Engine
Synthesizes probability metrics into operational directives (`DISPATCH`, `ALLOCATE`, `REPLENISH`).

### 5. Linear Resource Optimization
Uses **Google OR-Tools (GLOP)** to mathematically distribute limited resources across multiple zones to maximize covered Priority Scores, ensuring fairness when supplies are insufficient.

### 6. Dynamic Graph Routing
Uses **NetworkX** to represent road networks as spatial graphs. Calculates optimal delivery routes using Dijkstra/A* algorithms, with dynamic rerouting capabilities when roads are reported blocked mid-flight.

*(See [docs/ml_pipeline.md](docs/ml_pipeline.md) for detailed mathematical models).*

---

## 💻 Tech Stack

| Domain | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 14, React, Tailwind CSS, shadcn/ui, Recharts, React-Leaflet |
| **Backend** | Python, FastAPI, SQLAlchemy, Pydantic |
| **Machine Learning** | PyTorch, scikit-learn, XGBoost, spacy |
| **Optimization/Math** | Google OR-Tools, NetworkX |
| **Database** | PostgreSQL |
| **Infrastructure** | Docker, Docker Compose, n8n |

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- Git.

### 2. Start the Environment
Clone the repository and spin up the containers:
```bash
docker-compose up -d --build
```

### 3. Access the Application
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **Backend API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **n8n Orchestration (Optional):** [http://localhost:5678](http://localhost:5678)

### 4. Run the Simulation (Testing)
To populate the database with mock historical data and trigger a crisis scenario, run:
```bash
curl -X POST http://localhost:8000/api/v1/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"scenario_name": "CHENNAI_FLOOD", "affected_zones": [1, 2], "population_affected": 150000, "duration_days": 7}'
```

---

## 🔮 Future Enhancements
- Integration with satellite imagery (Computer Vision) for automated road blockage detection.
- Real-time GPS tracking for delivery trucks.
- Multilingual NLP support for local dialects during field report parsing.

---

## 📝 License
This project is developed for academic purposes. 
"# crisis-intelligence-platform" 
