from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Crisis(Base):
    __tablename__ = "crises"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # Flood, Cyclone, etc.
    severity = Column(String)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    affected_population = Column(Integer, default=0)
    status = Column(String)  # ACTIVE, RESOLVED, etc.

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    population = Column(Integer)
    vulnerability_score = Column(Float)
    accessibility_score = Column(Float)

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    capacity = Column(Float)
    operational_status = Column(String)  # ONLINE, OFFLINE, DAMAGED

    location = relationship("Location")

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)  # Medical, Food, Shelter
    unit = Column(String)
    criticality = Column(String)  # HIGH, MEDIUM, LOW
    shelf_life = Column(Integer, nullable=True)  # in days

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    quantity = Column(Float, default=0.0)
    reserved_quantity = Column(Float, default=0.0)
    minimum_threshold = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    warehouse = relationship("Warehouse")
    resource = relationship("Resource")

class DemandRecord(Base):
    __tablename__ = "demand_records"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    quantity = Column(Float)
    source = Column(String)

    location = relationship("Location")
    resource = relationship("Resource")

class DemandForecast(Base):
    __tablename__ = "demand_forecasts"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    forecast_timestamp = Column(DateTime)
    predicted_demand = Column(Float)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    confidence = Column(Float)
    model_version = Column(String)

class CrisisReport(Base):
    __tablename__ = "crisis_reports"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String)  # TWITTER, VOLUNTEER, NEWS
    raw_text = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    processed_status = Column(String, default="PENDING")

class CrisisSignal(Base):
    __tablename__ = "crisis_signals"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("crisis_reports.id"))
    location = Column(String, nullable=True)
    resource = Column(String, nullable=True)
    urgency = Column(String)
    affected_population = Column(Integer, nullable=True)
    event_type = Column(String)
    confidence = Column(Float)

    report = relationship("CrisisReport")

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    source_location = Column(Integer, ForeignKey("locations.id"))
    destination_location = Column(Integer, ForeignKey("locations.id"))
    distance = Column(Float)
    estimated_time = Column(Float)
    risk_score = Column(Float)
    status = Column(String)

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    quantity = Column(Float)
    source = Column(Integer, ForeignKey("locations.id"))
    destination = Column(Integer, ForeignKey("locations.id"))
    vehicle = Column(String)
    route = Column(Integer, ForeignKey("routes.id"))
    status = Column(String)
    eta = Column(DateTime, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    severity = Column(String)
    message = Column(String)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class Decision(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True, index=True)
    decision_type = Column(String)
    input_state = Column(JSON)
    recommendation = Column(JSON)
    confidence = Column(Float)
    explanation = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SupplyChainLedger(Base):
    __tablename__ = "supply_chain_ledger"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    quantity = Column(Float)
    sender = Column(String)
    receiver = Column(String)
    previous_hash = Column(String)
    current_hash = Column(String, unique=True, index=True)

    resource = relationship("Resource")
