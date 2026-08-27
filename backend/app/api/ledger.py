from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.core_models import SupplyChainLedger
from app.services.blockchain_service import verify_chain, add_transaction
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class LedgerTransactionCreate(BaseModel):
    resource_id: int
    quantity: float
    sender: str
    receiver: str

class LedgerBlockResponse(BaseModel):
    id: int
    timestamp: datetime
    resource_id: int
    quantity: float
    sender: str
    receiver: str
    previous_hash: str
    current_hash: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[LedgerBlockResponse])
def get_ledger(db: Session = Depends(get_db)):
    """Retrieve the entire supply chain blockchain."""
    blocks = db.query(SupplyChainLedger).order_by(SupplyChainLedger.id.asc()).all()
    return blocks

@router.post("/add", response_model=LedgerBlockResponse)
def add_ledger_transaction(transaction: LedgerTransactionCreate, db: Session = Depends(get_db)):
    """Add a new transaction to the blockchain ledger."""
    new_block = add_transaction(
        db=db,
        resource_id=transaction.resource_id,
        quantity=transaction.quantity,
        sender=transaction.sender,
        receiver=transaction.receiver
    )
    return new_block

@router.get("/verify")
def verify_ledger(db: Session = Depends(get_db)):
    """Verify the cryptographic integrity of the blockchain."""
    is_valid = verify_chain(db)
    if is_valid:
        return {"status": "success", "message": "Blockchain is valid and untampered."}
    else:
        raise HTTPException(status_code=400, detail="Blockchain integrity compromised!")
