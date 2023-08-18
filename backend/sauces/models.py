from django.db import models
from django.db.models import Func
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import BTreeIndex

from polymorphic.models import PolymorphicModel

from sauces.utils.fields import BitField

# Create your models here.


class Sauce(models.Model):
    class Meta:
        unique_together = ["source", "source_site_id"]

    class SauceType(models.IntegerChoices):
        ART_STATIC = 0, "Art"
        ART_ANIMATED = 1, "Animated"
        MANGA = 2, "Manga"
        DOUJINSHI = 3, "Doujinshi"
        ANIME = 4, "Anime"

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

    type = models.PositiveSmallIntegerField(
        choices=SauceType.choices, default=SauceType.ART_STATIC
    )
    is_nsfw = models.BooleanField(default=False)

    downloaded = models.BooleanField(default=False, db_index=True)
    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Hash(models.Model):
    class HashingMethod(models.IntegerChoices):
        PERCEPTUAL = 0, "Perceptual"
        AVERAGE = 1, "Average"
        DIFERENTIAL = 2, "Differential"
        WAVELET = 3, "Wavelet"

    class Meta:
        verbose_name = "Hash"
        verbose_name_plural = "Hashes"
        indexes = [
            BTreeIndex(
                "bits",
                condition=models.Q(
                    models.Q(Func("bits", function="BIT_LENGTH") == 2 ** (i // 4 + 3))
                    and models.Q(method=i % 4)
                ),
                name="hash_{}_{}_idx".format(i % 4, 2 ** (i // 4 + 3)),
            )
            for i in range(
                4 * 4
            )  # {amount of different hash sizes, in this case 8, 16, 32, and 64} * {amount of different hashing methods, 0, 1, 2, and 3}
        ]

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


class Artist(models.Model):
    names = ArrayField(
        models.CharField(max_length=255, null=False), db_index=True, blank=True
    )
    links = ArrayField(models.URLField(max_length=255, null=False), blank=False)
    tags = ArrayField(
        models.CharField(max_length=255, null=False, blank=True),
        default=list,
        db_index=True,
        blank=False,
    )
    sauces = models.ManyToManyField("Sauce", related_name="artists", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.names[0]
