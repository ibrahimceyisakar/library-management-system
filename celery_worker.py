from celery import Celery
import os

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery = Celery("tasks", broker=redis_url, backend=redis_url)

# Load Celery configuration
celery.config_from_object('app.config.celery_config')

# Include the tasks module directly
celery.conf.update(
    task_routes={
        'app.tasks.library_tasks.*': {'queue': 'notifications'},
    }
)

# Import tasks explicitly
from app.tasks import library_tasks

if __name__ == '__main__':
    celery.start()
