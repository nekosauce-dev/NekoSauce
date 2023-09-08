import secrets

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


def generate_api_key():
    return secrets.token_urlsafe(64)


class User(AbstractUser):
    donation = models.FloatField(default=0.0)
    donation_date = models.DateTimeField(null=True)

    api_key = models.CharField(default=generate_api_key, max_length=86)
