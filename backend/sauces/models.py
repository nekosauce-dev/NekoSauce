from django.db import models
from django.contrib.postgres.fields import ArrayField

from polymorphic.models import PolymorphicModel

from sauces.utils.fields import BitField

# Create your models here.


class Sauce(models.Model):
    class Meta:
        unique_together = ["source", "source_site_id"]

    title = models.CharField(max_length=255)

    site_urls = ArrayField(models.URLField(max_length=255, null=False))
    api_urls = ArrayField(models.URLField(max_length=255, null=False))
    file_urls = ArrayField(models.URLField(max_length=255, null=False))

    hashes = models.ManyToManyField("sauces.Hash", related_name="sauces")

    source = models.ForeignKey(
        "sauces.Source", on_delete=models.CASCADE, null=False, related_name="sauces"
    )
    source_site_id = models.CharField(max_length=255, null=False)
    tags = ArrayField(
        models.CharField(max_length=255, null=False, blank=True), default=list
    )

    downloaded = models.BooleanField(default=False)
    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Hash(models.Model):
    class Meta:
        verbose_name = "Hash"
        verbose_name_plural = "Hashes"

    class HashingMethod(models.IntegerChoices):
        PERCEPTUAL = 0, "Perceptual"
        AVERAGE = 1, "Average"
        DIFERENTIAL = 2, "Differential"
        WAVELET = 3, "Wavelet"

    bits = BitField(
        max_length=4096, unique=True, null=False, blank=False, primary_key=True
    )
    method = models.IntegerField(
        choices=HashingMethod.choices, default=HashingMethod.PERCEPTUAL
    )


class Source(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(max_length=255)
    api_docs = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
