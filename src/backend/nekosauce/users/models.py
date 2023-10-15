import secrets

from django.db import models
from django.contrib.auth.models import AbstractUser


def generate_api_key():
    return secrets.token_urlsafe(64)


class User(AbstractUser):
    class DonationTier(models.IntegerChoices):
        NONE = 0, "None"
        CHAN = 3, "Supporter-chan"
        SENPAI = 5, "Supporter-senpai"
        SAMA = 10, "Supporter-sama"

    donation = models.FloatField(
        default=DonationTier.NONE, choices=DonationTier.choices
    )
    donation_date = models.DateTimeField(null=True)

    api_key = models.CharField(default=generate_api_key, max_length=86, db_index=True)
