from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.core_models import DemandRecord, Location, Resource
from app.schemas.demand import DemandCreate

class DemandService:
    def get_demand_records(self, db: Session, location_id: int = None, resource_id: int = None, skip: int = 0, limit: int = 100):
        query = db.query(DemandRecord)
        if location_id:
            query = query.filter(DemandRecord.location_id == location_id)
        if resource_id:
            query = query.filter(DemandRecord.resource_id == resource_id)
            
        query = query.order_by(DemandRecord.timestamp.desc())
        return query.offset(skip).limit(limit).all()

    def create_demand_record(self, db: Session, demand_in: DemandCreate):
        location = db.query(Location).filter(Location.id == demand_in.location_id).first()
        if not location:
            return None, "Location not found"
            
        resource = db.query(Resource).filter(Resource.id == demand_in.resource_id).first()
        if not resource:
            return None, "Resource not found"
            
        demand = DemandRecord(
            location_id=demand_in.location_id,
            resource_id=demand_in.resource_id,
            quantity=demand_in.quantity,
            source=demand_in.source,
            timestamp=datetime.now(timezone.utc)
        )
        
        db.add(demand)
        db.commit()
        db.refresh(demand)
        return demand, None

demand_service = DemandService()
