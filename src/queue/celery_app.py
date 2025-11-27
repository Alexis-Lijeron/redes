"""
Configuración de Celery para procesamiento asíncrono
"""
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# URL de Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Crear aplicación Celery
celery_app = Celery(
    "social_media_publisher",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.queue.tasks"]
)

# Configuración
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutos máximo por tarea
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

if __name__ == "__main__":
    celery_app.start()
