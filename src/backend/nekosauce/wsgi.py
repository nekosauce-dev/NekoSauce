"""
WSGI config for nekosauce project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.apps import apps
from django.conf import settings
from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nekosauce.settings")
apps.populate(settings.INSTALLED_APPS)

application = get_wsgi_application()


from nekosauce.sauces.tree import load_tree

load_tree()
