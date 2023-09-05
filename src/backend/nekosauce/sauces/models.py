import io

from django.db import models
from django.db.models import Func
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import BTreeIndex

from PIL import Image, ImageFile

import imagehash

from nekosauce.sauces.utils.fields import BitField
from nekosauce.sauces.utils.hashing import hash_to_bits


ImageFile.LOAD_TRUNCATED_IMAGES = True


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

    hashes_8bits = models.ManyToManyField("sauces.Hash8Bits", related_name="sauces")
    hashes_16bits = models.ManyToManyField("sauces.Hash16Bits", related_name="sauces")
    hashes_32bits = models.ManyToManyField("sauces.Hash32Bits", related_name="sauces")
    hashes_64bits = models.ManyToManyField("sauces.Hash64Bits", related_name="sauces")

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

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def calc_hashes(self, save: bool = True) -> bool:
        from nekosauce.sauces.sources import get_downloader

        downloaders = [(get_downloader(url), url) for url in self.file_urls]
        downloaders = [d for d in downloaders if d[0] is not None]

        downloader, url = downloaders[0] if downloaders else (None, None)

        if downloader is None:
            return False, "No downloader found for URLs {}".format(
                ", ".join(self.file_urls)
            )

        img = Image.open(io.BytesIO(downloader().download(url)))

        hash_model_from_bits = {
            8: Hash8Bits,
            16: Hash16Bits,
            32: Hash32Bits,
            64: Hash64Bits,
        }

        hashes = {algorithm: {} for algorithm in Hash.Algorithm}

        for size in [8, 16, 32, 64]:
            for algorithm in [
                (Hash.Algorithm.PERCEPTUAL, imagehash.phash),
                (Hash.Algorithm.AVERAGE, imagehash.average_hash),
                (Hash.Algorithm.DIFFERENTIAL, imagehash.dhash),
                (Hash.Algorithm.WAVELET, imagehash.whash),
            ]:
                bits = hash_to_bits(algorithm[1](img, hash_size=size))
                new_hash, _ = hash_model_from_bits[size].objects.update_or_create(
                    bits=bits,
                    algorithm=algorithm[0],
                )
                hashes[algorithm[0]][size] = new_hash

        for algorithm in Hash.Algorithm:
            for size in [8, 16, 32, 64]:
                new_hash = hashes[algorithm][size]
                getattr(self, f"hashes_{size}bits").add(new_hash)

        self.downloaded = True

        if save:
            self.save()

        return True, None


class Hash(models.Model):
    class Algorithm(models.IntegerChoices):
        PERCEPTUAL = 0, "Perceptual"
        AVERAGE = 1, "Average"
        DIFFERENTIAL = 2, "Differential"
        WAVELET = 3, "Wavelet"

    class Meta:
        verbose_name = "Hash"
        verbose_name_plural = "Hashes"
        unique_together = ["bits", "algorithm"]
        abstract = True

    algorithm = models.IntegerField(
        choices=Algorithm.choices, default=Algorithm.PERCEPTUAL
    )

    def __str__(self):
        return str(self.bits)


class Hash8Bits(Hash):
    class Meta(Hash.Meta):
        abstract = False
        verbose_name = "Hash (8^2 Bits)"
        verbose_name_plural = "Hashes (8^2 Bits)"
        indexes = [
            BTreeIndex(
                ["bits"],
                condition=models.Q(algorithm=algorithm),
                name=f"hash8_{algorithm}_idx",
            )
            for algorithm in range(len(Hash.Algorithm.choices))
        ]

    bits = BitField(max_length=8**2, null=False, blank=False, db_index=True)


class Hash16Bits(Hash):
    class Meta(Hash.Meta):
        abstract = False
        verbose_name = "Hash (16^2 Bits)"
        verbose_name_plural = "Hashes (16^2 Bits)"
        indexes = [
            BTreeIndex(
                ["bits"],
                condition=models.Q(algorithm=algorithm),
                name=f"hash16_{algorithm}_idx",
            )
            for algorithm in range(len(Hash.Algorithm.choices))
        ]

    bits = BitField(max_length=16**2, null=False, blank=False, db_index=True)


class Hash32Bits(Hash):
    class Meta(Hash.Meta):
        abstract = False
        verbose_name = "Hash (32^2 Bits)"
        verbose_name_plural = "Hashes (32^2 Bits)"
        indexes = [
            BTreeIndex(
                ["bits"],
                condition=models.Q(algorithm=algorithm),
                name=f"hash32_{algorithm}_idx",
            )
            for algorithm in range(len(Hash.Algorithm.choices))
        ]

    bits = BitField(max_length=32**2, null=False, blank=False, db_index=True)


class Hash64Bits(Hash):
    class Meta(Hash.Meta):
        abstract = False
        verbose_name = "Hash (64^2 Bits)"
        verbose_name_plural = "Hashes (64^2 Bits)"
        indexes = [
            BTreeIndex(
                ["bits"],
                condition=models.Q(algorithm=algorithm),
                name=f"hash64_{algorithm}_idx",
            )
            for algorithm in range(len(Hash.Algorithm.choices))
        ]

    bits = BitField(max_length=64**2, null=False, blank=False, db_index=True)


class Source(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(max_length=255)
    api_docs = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
