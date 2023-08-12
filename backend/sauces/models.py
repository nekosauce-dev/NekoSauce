from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Sauce(models.Model):
    class SauceType(models.TextChoices):
        ART = "art"
        ANIME = "anime"
        MANGA = "manga"

    title = models.CharField(max_length=255)
    sauce_type = models.CharField(
        choices=SauceType.choices, default=SauceType.ART, max_length=5, null=False
    )
    site_urls = ArrayField(models.URLField(max_length=255, null=False))
    api_urls = ArrayField(models.URLField(max_length=255, null=False))
    file_url = models.URLField(max_length=255, null=False)
    source = models.ForeignKey(
        "sauces.Source", on_delete=models.CASCADE, null=False, related_name="sauces"
    )
    site_id = models.CharField(max_length=255, null=False)
    artist = models.ForeignKey("sauces.Artist", on_delete=models.SET_NULL, null=True)
    height = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()

    ahash_8 = models.CharField(max_length=16, null=True, blank=True)
    ahash_16 = models.CharField(max_length=64, null=True, blank=True)
    ahash_32 = models.CharField(max_length=256, null=True, blank=True)
    ahash_64 = models.CharField(max_length=1024, null=True, blank=True)
    ahash_cr = ArrayField(
        models.CharField(max_length=8, null=False),
        max_length=6,
        blank=True,
        default=list,
    )
    phash_8 = models.CharField(max_length=64, null=True, blank=True)
    phash_16 = models.CharField(max_length=256, null=True, blank=True)
    phash_32 = models.CharField(max_length=1024, null=True, blank=True)
    phash_64 = models.CharField(max_length=4096, null=True, blank=True)
    phash_cr = ArrayField(
        models.CharField(max_length=8, null=False),
        max_length=6,
        blank=True,
        default=list,
    )
    dhash_8 = models.CharField(max_length=64, null=True, blank=True)
    dhash_16 = models.CharField(max_length=256, null=True, blank=True)
    dhash_32 = models.CharField(max_length=1024, null=True, blank=True)
    dhash_64 = models.CharField(max_length=4096, null=True, blank=True)
    dhash_cr = ArrayField(
        models.CharField(max_length=8, null=False),
        max_length=6,
        blank=True,
        default=list,
    )

    def __str__(self):
        return self.title


class Artist(models.Model):
    names = ArrayField(models.CharField(max_length=255, unique=True), blank=False)
    site_urls = ArrayField(models.URLField(max_length=255, null=False))
    api_urls = ArrayField(models.URLField(max_length=255, null=False))

    def __str__(self):
        return self.names[0]


class Source(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(max_length=255)
    api_docs = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
