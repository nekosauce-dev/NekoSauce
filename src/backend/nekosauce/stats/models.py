from django.db import models

# Create your models here.


class Statistic(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=["resource", "attribute"]),
        ]

    resource = models.CharField(max_length=255, editable=False)
    attribute = models.CharField(max_length=255, editable=False)
    value = models.CharField(max_length=255, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
