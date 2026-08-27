import os

model_code = """
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
"""

with open('app/models/core_models.py', 'a') as f:
    f.write(model_code)
print('Successfully appended to core_models.py')
