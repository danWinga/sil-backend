# config/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# pull broker URL from settings.RABBITMQ_URL
app.conf.broker_url = os.environ.get("RABBITMQ_URL")

# use Django settings prefixed with CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# auto-discover @shared_task in your apps
app.autodiscover_tasks()