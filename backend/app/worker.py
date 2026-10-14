from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "price_comparator",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "check-alerts-every-hour": {
            "task": "app.tasks.alert_tasks.check_alerts",
            "schedule": 3600.0,  # 1 hour
        },
        "cleanup-old-prices-daily": {
            "task": "app.tasks.cleanup_tasks.cleanup_old_prices",
            "schedule": 86400.0,  # 24 hours
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])