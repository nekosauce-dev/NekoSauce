from celery import Celery

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nekosauce.settings")

from django.conf import settings


app = Celery("nekosauce")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
