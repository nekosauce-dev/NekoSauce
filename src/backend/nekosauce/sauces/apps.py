import sys

from django.apps import AppConfig
from django.conf import settings


class SaucesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nekosauce.sauces"

    def ready(self):
        if "collectstatic" in sys.argv:
            return

        from nekosauce.sauces import tree
        tree.load()
