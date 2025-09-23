from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "task_scheduler",
    broker=settings.redis_url,
    backend=settings.celery_result_backend,
    include=['app.celery_app.tasks']
)

celery_app.conf.update(
    task_default_queue=settings.celery_task_default_queue,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_max_tasks_per_child=1000,
    timezone="UTC",
    enable_utc=True,
    # Define priority queues
    task_routes={
        'app.celery_app.tasks.execute_task_high_priority': {'queue': 'high_priority'},
        'app.celery_app.tasks.execute_task_medium_priority': {'queue': 'medium_priority'},
        'app.celery_app.tasks.execute_task_low_priority': {'queue': 'low_priority'},
        'app.celery_app.tasks.schedule_recurring_tasks': {'queue': 'medium_priority'},
    },
    beat_schedule={
        "scan-recurrences": {
            "task": "app.celery_app.tasks.schedule_recurring_tasks",
            "schedule": settings.recurrence_scan_interval_seconds,
        }
    },
)
