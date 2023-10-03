from django.core.validators import MinValueValidator, MaxValueValidator

from rest_framework import serializers

from nekosauce.sauces.utils.registry import registry


class SearchQuerySerializer(serializers.Serializer):
    url = serializers.URLField(required=False)
    limit = serializers.IntegerField(
        default=10, validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    threshold = serializers.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)], required=False
    )
    sources = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[
                source["id"] for source in registry["sources"]
            ]
        ),
        required=False,
    )
    nsfw = serializers.BooleanField(required=False)
    types = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[
                t["id"] for t in registry["sauce_types"]
            ]
        ),
        required=False,
    )
