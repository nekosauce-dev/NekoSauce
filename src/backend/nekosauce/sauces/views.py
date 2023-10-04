import io

from django.conf import settings
from django.db.models import Func, F, Value
from django.db.models.expressions import RawSQL

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from PIL import Image, UnidentifiedImageError

import requests

import imagehash

from nekosauce.exceptions import ValidationError, DownloadError
from nekosauce.sauces.models import Sauce
from nekosauce.sauces.serializers import SearchQuerySerializer
from nekosauce.sauces.utils.hashing import hash_to_bits
from nekosauce.sauces.utils.registry import registry, get_sauce_type


class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = SearchQuerySerializer(data=request.GET)

        if not serializer.is_valid():
            raise ValidationError(
                detail=f"The following fields are invalid: {', '.join(list(serializer.errors.keys()))}"
            )

        file_obj = request.data.get("file")

        if not file_obj and not serializer.validated_data.get("url"):
            raise ValidationError(detail="Either a file or a URL is required.")

        if not file_obj:
            r = requests.get(
                serializer.validated_data.get("url"),
                headers={"User-Agent": f"NekoSauce/{settings.VERSION}"},
                stream=True,
                timeout=5,
            )

            try:
                r.raise_for_status()
            except:
                raise DownloadError()

            file_bytes = b""
            for chunk in r.iter_content(chunk_size=1024):
                file_bytes += chunk

                if len(file_bytes) > 1024 * 1024 * 1024:
                    break

            file_obj = io.BytesIO(file_bytes)

        try:
            img = Image.open(file_obj)
        except UnidentifiedImageError:
            raise ValidationError(
                detail="This doesn't seem to be an image! U sure u've checked correctly? Nya!",
                code="invalid_image",
            )

        image_hash = imagehash.whash(img, hash_size=16)
        image_hash_bits = hash_to_bits(image_hash)

        limit = serializer.validated_data["limit"]

        results = Sauce.objects.filter(hash__isnull=False).annotate(
            similarity=Func(
                F("hash"), RawSQL("B'%s'" % image_hash_bits, ()), function="HAMMING"
            )
        ).order_by("-similarity")[:limit]

        return Response(
            {
                "data": [
                    {
                        "id": sauce.id,
                        "similarity": sauce.similarity,
                        "hash": hex(int(sauce.hash, 2))[2:],
                        "sha512": sauce.sha512.hex(),
                        "urls": {
                            "site": sauce.site_urls,
                            "api": sauce.api_urls,
                            "file": sauce.file_urls,
                        },
                        "source": sauce.source_id,
                        "source_site_id": sauce.source_site_id,
                        "tags": sauce.tags,
                        "type": get_sauce_type(sauce.type),
                        "is_nsfw": sauce.is_nsfw,
                        "file_meta": {
                            "height": sauce.height,
                            "width": sauce.width,
                            "mimetype": "image/webp",
                        },
                        "created_at": sauce.created_at,
                        "updated_at": sauce.updated_at,
                    }
                    for sauce in results
                ][:limit],
                "meta": {
                    "count": len(results),
                    "hash": hex(int(image_hash_bits, 2))[2:],
                    "upload": serializer.validated_data.get("url"),
                },
            }
        )


class SourceView(APIView):
    def get(self, request):
        return Response(
            {
                "data": registry["sources"],
                "meta": {
                    "count": len(registry["sources"]),
                },
            }
        )
