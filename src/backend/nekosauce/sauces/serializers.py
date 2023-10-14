from django.core.validators import MinValueValidator, MaxValueValidator

from rest_framework import serializers

from nekosauce.sauces.utils.registry import registry


class SourcesField(serializers.Field):
    def to_representation(self, value):
        return ','.join(value)

    def to_internal_value(self, data):
        ids = [i.strip() for i in data.split(',')]
        valid_source_ids = [source["id"] for source in registry["sources"]]

        for i in ids:
            if not i.isnumeric():
                raise serializers.ValidationError(detail="Source IDs must be numeric. One of them doesn't seem to be numeric,")
            if int(i) not in valid_source_ids:
                raise serializers.ValidationError(detail="Invalid source ID. Check the available ones at `/api/sources`, nyan!")

        return [int(id) for id in ids]


class SearchQuerySerializer(serializers.Serializer):
    url = serializers.URLField(required=False)
    limit = serializers.IntegerField(
        default=10, validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    threshold = serializers.FloatField(
        validators=[MinValueValidator(1), MaxValueValidator(100)], required=False
    )
    sources = SourcesField(required=False, default=','.join([str(source["id"]) for source in registry["sources"]]))
    nsfw = serializers.BooleanField(required=False)
