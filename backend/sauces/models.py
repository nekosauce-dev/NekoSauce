from django.db import models
from django.contrib.postgres.fields import ArrayField

from polymorphic.models import PolymorphicModel

from sauces.utils.fields import BitField

# Create your models here.


class Sauce(PolymorphicModel):
    title = models.CharField(max_length=255)

    site_urls = ArrayField(models.URLField(max_length=255, null=False))
    api_urls = ArrayField(models.URLField(max_length=255, null=False))
    file_urls = ArrayField(models.URLField(max_length=255, null=False))

    hashes = models.ManyToManyField("sauces.Hash", related_name="sauces")

    uploaders = models.ManyToManyField("sauces.Uploader", related_name="sauces")

    source = models.ForeignKey(
        "sauces.Source", on_delete=models.CASCADE, null=False, related_name="sauces"
    )
    source_site_id = models.CharField(max_length=255, null=False)
    tags = ArrayField(
        models.CharField(max_length=255, null=False, blank=True), default=list
    )

    downloaded = models.BooleanField(default=False)
    height = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.title


class Hash(models.Model):
    class Meta:
        verbose_name = "Hash"
        verbose_name_plural = "Hashes"

    class HashingMethod(models.IntegerChoices):
        PERCEPTUAL = 0, "Perceptual Hash"
        AVERAGE = 1, "Average Hash"
        DIFERENTIAL = 2, "Differential Hash"

    bits = BitField(
        max_length=4096, unique=True, null=False, blank=False, primary_key=True
    )
    method = models.IntegerField(
        choices=HashingMethod.choices, default=HashingMethod.AVERAGE
    )
    crop_resistant = models.BooleanField(default=False)


class ArtSauce(Sauce):
    artist = models.ForeignKey(
        "sauces.Artist", on_delete=models.CASCADE, null=True, related_name="art_sauces"
    )


class MangaSauce(Sauce):
    artist = models.ForeignKey(
        "sauces.Artist",
        on_delete=models.CASCADE,
        null=False,
        related_name="manga_sauces",
    )


class AnimeSauce(Sauce):
    pass


class Entity(PolymorphicModel):
    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
    
    names = ArrayField(models.CharField(max_length=255, unique=True), blank=False)
    links = ArrayField(
        models.URLField(max_length=255, null=False, unique=True), blank=False
    )
    tags = ArrayField(
        models.CharField(max_length=255, null=False, blank=True), default=list
    )


class Artist(Entity):
    direct_uploader = models.OneToOneField(
        "sauces.Uploader", related_name="artist", on_delete=models.SET_NULL, null=True
    )


class Uploader(Entity):
    class Type(models.IntegerChoices):
        INDIVIDUAL = 0, "Individual"
        SCANLATION_GROUP = 1, "Scanlation Group"

    type = models.IntegerField(choices=Type.choices, default=Type.INDIVIDUAL)


class Source(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(max_length=255)
    api_docs = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
