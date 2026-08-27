# Pure Software Architecture

The platform follows a highly decoupled, pure software microservice architecture using a monorepo structure. There are **zero hardware or IoT dependencies**, making it highly scalable and rapidly deployable in cloud environments.

## Core Software Layers (Matching Review 0 PPT)

### 1. Data Ingestion Layer (Webhooks & APIs)
- Instead of hardware sensors, the system relies entirely on digital telemetry and crowdsourced data.
- Sources include Simulated JSON Crisis Data, Twitter API Feeds (Social Media), and Crowdsourced Web Forms.

### 2. API Gateway (FastAPI)
- High-performance asynchronous Python API.
- Handles routing, validation (via Pydantic), and acts as the central nerve center for incoming SOS requests.

### 3. Intelligence Processing Engine
- **NLP Engine (spaCy):** Extracts actionable entities (`Location`, `Resource`, `Urgency`) from unstructured text.
- **LSTM Forecast Model (PyTorch):** Processes rolling window chunks of time-series data to predict sudden spikes in relief material demand.
- **Priority Matrix:** Computes a normalized Vulnerability Score based on urgency and population density.

### 4. Database Layer
- **PostgreSQL:** Relational store managed via SQLAlchemy and Alembic. Stores `locations`, `inventory`, `forecasts`, and `signals`.
- **Redis (Optional Cache):** Used for fast retrieval of live routing coordinates and token caching.

### 5. Optimization & Routing Engine
- **Google OR-Tools (GLOP Optimizer):** Formulates resource scarcity as a linear programming problem and mathematically calculates equitable allocations.
- **NetworkX Dynamic Graph Routing:** Represents the disaster zone as a spatial graph and uses the A* algorithm to route vehicles around digitally reported blockages.

### 6. Presentation Layer (Frontend)
- **Next.js 14 Dashboard:** Built with React and Tailwind CSS.
- **Leaflet Maps UI:** Real-time spatial visualization of the calculated routes and heatmaps.
