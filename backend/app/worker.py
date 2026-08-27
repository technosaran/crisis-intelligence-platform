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
    from app.optimization.allocation.optimizer import allocation_optimizer
    # Run the heavy mathematical optimization
    result = allocation_optimizer.optimize_multi_warehouse_allocation(
        warehouses=warehouses_data,
        demands=demands_data,
        fairness_ratio=fairness_ratio
    )
    return result
