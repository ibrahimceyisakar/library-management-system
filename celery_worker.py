from celery import Celery
import os

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery = Celery("library_tasks", broker=redis_url, backend=redis_url)

# Load Celery configuration
celery.config_from_object('app.config.celery_config')

# Auto-discover tasks in the specified packages
celery.autodiscover_tasks(['app.tasks'])

if __name__ == '__main__':
    celery.start()
