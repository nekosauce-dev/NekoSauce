import os

from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nekosauce.settings")

from django.conf import settings


app = Celery("nekosauce", broker=f"redis://{'nekosauce' if not settings.DEBUG else 'localhost'}:6379/0")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
