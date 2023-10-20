import io

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
                headers={"User-Agent": "NekoSauce"},
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

        query = requests.get(
            "http://127.0.0.1:7171/find",
            params={
                "bits": image_hash_bits,
                "distance": int(256 * (serializer.validated_data["threshold"] / 100)),
            },
        ).json()

        results = Sauce.objects.filter(
            id__in=[item["id"] for item in query[: serializer.validated_data["limit"]]],
        )

        if serializer.validated_data["nsfw"] is not None:
            results = results.filter(is_nsfw=serializer.validated_data["nsfw"])

        get_similarity = lambda x: 100 - (
            next((item for item in query if item["id"] == x.id), None)["d"] / 100 * 256
        )

        return Response(
            {
                "data": sorted(
                    [
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
                        }
                        for sauce in results
                    ],
                    key=get_similarity,
                ),
            }
        )


class SourceView(APIView):
    def get(self, request):
        return Response(
            {
                "data": registry["sources"],
            }
        )
