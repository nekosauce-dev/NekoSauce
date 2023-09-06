import io
import hashlib

from django.db import models
from django.db.models import Func
from django.core.files.storage import default_storage
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import BTreeIndex

from PIL import Image, ImageFile

import imagehash

from nekosauce.sauces.utils.fields import BitField
from nekosauce.sauces.utils.hashing import hash_to_bits


ImageFile.LOAD_TRUNCATED_IMAGES = True


def get_thumbnail_size(width: int, height: int, min_size: int = 256) -> tuple[int, int]:
    """Calculates the thumbnail size. Either width or height will match the min_size and the other one will adapt to match the aspect ratio.

    Args:
        width (int): The image's original width.
        height (int): The image's original height.
        min_size (int, optional): The image's minimum width/height. Defaults to 512.

    Returns:
        tuple: The thumbnail width/height.
    """

    if width < height:
        return min_size, int((min_size * height) / width)
    return int((min_size * width) / height), min_size


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

    hash = models.ForeignKey(
        "sauces.Hash",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sauces",
    )
    sha512_hash = models.CharField(
        max_length=128,
        db_index=True,
        null=True
    )

    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def calc_hash(self, save: bool = True) -> bool:
        from nekosauce.sauces.sources import get_downloader

        downloaders = [(get_downloader(url), url) for url in self.file_urls]
        downloaders = [d for d in downloaders if d[0] is not None]

        downloader, url = downloaders[0] if downloaders else (None, None)

        if downloader is None:
            return False, "No downloader found for URLs {}".format(
                ", ".join(self.file_urls)
            )

        img = Image.open(io.BytesIO(downloader().download(url)))

        self.height = img.height
        self.width = img.width

        self.hash, created = Hash.objects.get_or_create(
            bits=hash_to_bits(
                imagehash.whash(img, hash_size=16),
            )
        )

        if save:
            self.save()

        return True, None

    def download_thumbnail(self) -> None:
        from nekosauce.sauces.sources import get_downloader

        downloaders = [(get_downloader(url), url) for url in self.file_urls]
        downloaders = [d for d in downloaders if d[0] is not None]

        downloader, url = downloaders[0] if downloaders else (None, None)

        if downloader is None:
            return False, "No downloader found for URLs {}".format(
                ", ".join(self.file_urls)
            )

        response = downloader().download(url)

        sha512_hash = hashlib.sha512(response).hexdigest()

        img = Image.open(io.BytesIO(response))
        img.thumbnail(get_thumbnail_size(img.width, img.height))

        with io.BytesIO() as output:
            img.save(output, format="WEBP")
            output.seek(0)
            default_storage.save(
                f"images/thumbnails/{self.source.name.lower().replace(' ', '-')}/{sha512_hash}.webp",
                output,
            )

        self.sha512_hash = sha512_hash
        self.save()

        return None


class Hash(models.Model):
    class Meta:
        verbose_name = "Hash"
        verbose_name_plural = "Hashes"

    bits = BitField(max_length=16 ** 2, null=False, blank=False, unique=True, primary_key=True, editable=False)


class Source(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(max_length=255)
    api_docs = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
