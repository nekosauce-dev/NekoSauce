import io
import hashlib

from django.db import models
from django.db.models import Func, F, Q
from django.core.files.storage import default_storage
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import BTreeIndex

from PIL import Image, ImageFile

import imagehash

from nekosauce.sauces.utils.fields import BitField
from nekosauce.sauces.utils.hashing import hash_to_bits
from nekosauce.sauces.utils.registry import registry, get_source, get_sauce_type_by_name


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
        unique_together = ["source_id", "source_site_id"]
        indexes = [
            BTreeIndex(
                "hash",
                condition=Q(hash__isnull=False),
                name="sauces__hashes__idx",
            ),
            BTreeIndex(
                "source_id",
                "source_site_id",
                name="sauces__source_id__source_site_id__idx",
            )
        ] + [
            BTreeIndex(
                "hash",
                condition=Q(source_id=source_id, hash__isnull=False),
                name=f"sauces__{source_id}_hashes__idx",
            )
            for source_id in [source["id"] for source in registry["sources"]]
        ]

    site_urls = ArrayField(models.URLField(max_length=255, null=False))
    api_urls = ArrayField(models.URLField(max_length=255, null=False))
    file_urls = ArrayField(models.URLField(max_length=255, null=False))

    source_id = models.SmallIntegerField(
        choices=[(source["id"], source["name"]) for source in registry["sources"]],
        verbose_name="Source",
    )
    source_site_id = models.CharField(max_length=255, null=False)
    tags = ArrayField(
        models.CharField(max_length=255, null=False, blank=True), default=list
    )

    type = models.PositiveSmallIntegerField(
        choices=[(t["id"], t["name"]) for t in registry["sauce_types"]],
        default=get_sauce_type_by_name("illustration")["id"],
    )
    is_nsfw = models.BooleanField(default=False, null=True)

    hash = BitField(max_length=16**2, null=True)
    sha512 = models.BinaryField(null=True, editable=True)

    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def process(self, save: bool = True) -> bool:
        from nekosauce.sauces.sources import get_downloader

        if self.hash is not None and self.sha512 is not None:
            return False, None

        downloaders = [(get_downloader(url), url) for url in self.file_urls]
        downloaders = [d for d in downloaders if d[0] is not None]

        downloader, url = downloaders[0] if downloaders else (None, None)

        if downloader is None:
            return False, "No downloader found for URLs {}".format(
                ", ".join(self.file_urls)
            )

        img_bytes = downloader().download(url)
        img = Image.open(io.BytesIO(img_bytes))

        self.sha512 = (
            hashlib.sha512(img_bytes).digest()
            if self.sha512 is None
            else self.sha512
        )

        self.height = img.height
        self.width = img.width

        if self.hash is None:
            self.hash = hash_to_bits(
                imagehash.whash(img, hash_size=16),
            )

        thumbnail_path = f"images/thumbnails/{get_source(self.source_id)['name'].lower().replace(' ', '-')}/{self.sha512.hex()}.webp"

        if not default_storage.exists(thumbnail_path):
            img.thumbnail(get_thumbnail_size(img.width, img.height))
            with io.BytesIO() as output:
                img.save(output, format="WEBP")
                output.seek(0)
                default_storage.save(
                    thumbnail_path,
                    output,
                )

        if save:
            self.save()

        return True, None
