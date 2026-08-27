from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.simulation import router as simulation_router
from app.api.inventory import router as inventory_router
from app.api.demand import router as demand_router
from app.api.forecast import router as forecast_router
from app.api.nlp import router as nlp_router
from app.api.shortage import router as shortage_router
from app.api.priority import router as priority_router
from app.api.allocation import router as allocation_router
from app.api.routing import router as routing_router
from app.api.decision import router as decision_router
from app.api.alerts import router as alerts_router
from app.api.dashboard import router as dashboard_router
from app.api.websockets import router as websockets_router
from app.api.external import router as external_router
from app.api.ledger import router as ledger_router

from app.db.base import Base
from app.db.session import engine
from app import models  # Ensure models are registered

# Auto-create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(dashboard_router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])
app.include_router(simulation_router, prefix=f"{settings.API_V1_STR}/simulation", tags=["simulation"])
app.include_router(inventory_router, prefix=f"{settings.API_V1_STR}/inventory", tags=["inventory"])
app.include_router(demand_router, prefix=f"{settings.API_V1_STR}/demand", tags=["demand"])
app.include_router(forecast_router, prefix=f"{settings.API_V1_STR}/forecast", tags=["forecast"])
app.include_router(nlp_router, prefix=f"{settings.API_V1_STR}/nlp", tags=["nlp"])
app.include_router(shortage_router, prefix=f"{settings.API_V1_STR}/shortage", tags=["shortage"])
app.include_router(priority_router, prefix=f"{settings.API_V1_STR}/priority", tags=["priority"])
app.include_router(allocation_router, prefix=f"{settings.API_V1_STR}/allocation", tags=["allocation"])
app.include_router(routing_router, prefix=f"{settings.API_V1_STR}/routing", tags=["routing"])
app.include_router(decision_router, prefix=f"{settings.API_V1_STR}/decision", tags=["decision"])
app.include_router(alerts_router, prefix=f"{settings.API_V1_STR}/alerts", tags=["automation"])
app.include_router(websockets_router, prefix=settings.API_V1_STR)
app.include_router(external_router, prefix=f"{settings.API_V1_STR}/external", tags=["External"])
app.include_router(ledger_router, prefix=f"{settings.API_V1_STR}/ledger", tags=["ledger"])

@app.get("/")
def root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
