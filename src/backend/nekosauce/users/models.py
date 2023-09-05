from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    donation = models.FloatField(default=0.0)
    donation_date = models.DateTimeField(null=True)
