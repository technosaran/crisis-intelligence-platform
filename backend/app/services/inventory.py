from sqlalchemy.orm import Session
from app.models.core_models import Inventory, Warehouse, Resource
from app.schemas.inventory import InventoryCreate, InventoryUpdate

class InventoryService:
    def get_inventory(self, db: Session, warehouse_id: int = None, resource_id: int = None, skip: int = 0, limit: int = 100):
        query = db.query(Inventory)
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        if resource_id:
            query = query.filter(Inventory.resource_id == resource_id)
        return query.offset(skip).limit(limit).all()

    def create_inventory(self, db: Session, inventory_in: InventoryCreate):
        warehouse = db.query(Warehouse).filter(Warehouse.id == inventory_in.warehouse_id).first()
        if not warehouse:
            return None, "Warehouse not found"
            
        resource = db.query(Resource).filter(Resource.id == inventory_in.resource_id).first()
        if not resource:
            return None, "Resource not found"
            
        existing = db.query(Inventory).filter(
            Inventory.warehouse_id == inventory_in.warehouse_id,
            Inventory.resource_id == inventory_in.resource_id
        ).first()
        
        if existing:
            return None, "Inventory record already exists for this warehouse and resource. Use update instead."
            
        inventory = Inventory(
            warehouse_id=inventory_in.warehouse_id,
            resource_id=inventory_in.resource_id,
            quantity=inventory_in.quantity,
            reserved_quantity=inventory_in.reserved_quantity,
            minimum_threshold=inventory_in.minimum_threshold
        )
        db.add(inventory)
        db.commit()
        db.refresh(inventory)
        return inventory, None

    def update_inventory(self, db: Session, inventory_id: int, inventory_in: InventoryUpdate):
        inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
        if not inventory:
            return None, "Inventory record not found"
            
        update_data = inventory_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(inventory, field, value)
            
        db.add(inventory)
        db.commit()
        db.refresh(inventory)
        return inventory, None

inventory_service = InventoryService()
