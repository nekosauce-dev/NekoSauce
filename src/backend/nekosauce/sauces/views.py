import io

from django.conf import settings
from django.db.models import Func, F, Value
from django.db.models.expressions import RawSQL

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from PIL import Image

import requests

import imagehash

from nekosauce.exceptions import ValidationError, DownloadError
from nekosauce.sauces.models import (
    Sauce,
    Source,
    Hash,
)
from nekosauce.sauces.serializers import SearchQuerySerializer
from nekosauce.sauces.utils.hashing import hash_to_bits


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

        img = Image.open(file_obj)

        image_hash = imagehash.whash(img, hash_size=32)
        image_hash_bits = hash_to_bits(image_hash)

        limit = serializer.validated_data["limit"]

        results = (
            Hash.objects.prefetch_related("sauces__source")
            .annotate(
                similarity=Func(
                    F("bits"), RawSQL("B'%s'" % image_hash_bits, ()), function="HAMMING"
                )
            )
            .order_by("-similarity")[:limit]
        )

        sauces = []
        for hash in results:
            for sauce in hash.sauces.all():
                sauces.append((sauce, hash))

        return Response(
            {
                "data": [
                    {
                        "id": s.id,
                        "similarity": h.similarity,
                        "title": s.title,
                        "hash": hex(int(h.bits, 2))[2:],
                        "sha512_hash": s.sha512_hash,
                        "urls": {
                            "site": s.site_urls,
                            "api": s.api_urls,
                            "file": s.file_urls,
                        },
                        "source": {
                            "id": s.source.id,
                            "name": s.source.name,
                            "website": s.source.website,
                            "api_docs": s.source.api_docs,
                        },
                        "source_site_id": s.source_site_id,
                        "tags": s.tags,
                        "type": Sauce.SauceType(s.type).label.upper(),
                        "is_nsfw": s.is_nsfw,
                        "file_meta": {
                            "height": s.height,
                            "width": s.width,
                        },
                        "created_at": s.created_at,
                        "updated_at": s.updated_at,
                    }
                    for s, h in sauces
                ][:limit],
                "meta": {
                    "count": len(sauces),
                    "hash": hex(int(image_hash_bits, 2))[2:],
                    "upload": serializer.validated_data.get("url"),
                },
            }
        )


class SourceView(APIView):
    def get(self, request):
        return Response(
            {
                "data": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "website": s.website,
                        "api_docs": s.api_docs,
                        "enabled": s.enabled,
                    }
                    for s in Source.objects.all()
                ],
                "meta": {
                    "count": Source.objects.count(),
                },
            }
        )
