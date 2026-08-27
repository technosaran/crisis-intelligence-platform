import hashlib
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.core_models import SupplyChainLedger

def compute_hash(index: int, timestamp: str, resource_id: int, quantity: float, sender: str, receiver: str, previous_hash: str) -> str:
    """Computes a SHA-256 hash for a block of supply chain transaction."""
    block_string = json.dumps({
        "index": index,
        "timestamp": timestamp,
        "resource_id": resource_id,
        "quantity": quantity,
        "sender": sender,
        "receiver": receiver,
        "previous_hash": previous_hash
    }, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def get_last_block(db: Session) -> SupplyChainLedger:
    return db.query(SupplyChainLedger).order_by(SupplyChainLedger.id.desc()).first()

def add_transaction(db: Session, resource_id: int, quantity: float, sender: str, receiver: str) -> SupplyChainLedger:
    last_block = get_last_block(db)
    
    # Genesis block logic
    if last_block is None:
        index = 1
        previous_hash = "0" * 64
    else:
        index = last_block.id + 1
        previous_hash = last_block.current_hash
        
    timestamp = datetime.utcnow()
    current_hash = compute_hash(
        index=index,
        timestamp=timestamp.isoformat(),
        resource_id=resource_id,
        quantity=quantity,
        sender=sender,
        receiver=receiver,
        previous_hash=previous_hash
    )
    
    new_block = SupplyChainLedger(
        timestamp=timestamp,
        resource_id=resource_id,
        quantity=quantity,
        sender=sender,
        receiver=receiver,
        previous_hash=previous_hash,
        current_hash=current_hash
    )
    
    db.add(new_block)
    db.commit()
    db.refresh(new_block)
    return new_block

def verify_chain(db: Session) -> bool:
    """Verifies the integrity of the blockchain."""
    blocks = db.query(SupplyChainLedger).order_by(SupplyChainLedger.id.asc()).all()
    for i in range(1, len(blocks)):
        current = blocks[i]
        previous = blocks[i-1]
        
        # 1. Check if previous_hash matches
        if current.previous_hash != previous.current_hash:
            return False
            
        # 2. Recompute current hash to ensure data wasn't tampered
        recomputed_hash = compute_hash(
            index=current.id,
            timestamp=current.timestamp.isoformat(),
            resource_id=current.resource_id,
            quantity=current.quantity,
            sender=current.sender,
            receiver=current.receiver,
            previous_hash=current.previous_hash
        )
        if current.current_hash != recomputed_hash:
            return False
            
    return True
