import os
from celery import Celery

redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "crisis_worker",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="optimize_allocation_task")
def optimize_allocation_task(warehouses_data, demands_data, fairness_ratio):
    """
    Runs the heavy OR-Tools LP optimization in a background Celery worker.
    
    NOTE: This task receives pre-fetched data (dicts) from the API layer.
    It does NOT need a DB session because the optimization is pure computation.
    If future tasks need DB access, create a session via:
        from app.db.session import SessionLocal
        db = SessionLocal()
        try: ... finally: db.close()
    """
    from app.optimization.allocation.optimizer import allocation_optimizer
    # Run the heavy mathematical optimization
    result = allocation_optimizer.optimize_multi_warehouse_allocation(
        warehouses=warehouses_data,
        demands=demands_data,
        fairness_ratio=fairness_ratio
    )
    return result
