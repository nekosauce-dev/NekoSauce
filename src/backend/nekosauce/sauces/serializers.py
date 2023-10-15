from django.core.validators import MinValueValidator, MaxValueValidator

from rest_framework import serializers

from nekosauce.sauces.utils.registry import registry


class SourcesField(serializers.Field):
    def to_representation(self, value):
        return ",".join(value)

    def to_internal_value(self, data):
        ids = [i.strip() for i in data.split(",")]
        valid_source_ids = [source["id"] for source in registry["sources"]]

        for i in ids:
            if not i.isnumeric():
                raise serializers.ValidationError(
                    detail="Source IDs must be numeric. One of them doesn't seem to be numeric,"
                )
            if int(i) not in valid_source_ids:
                raise serializers.ValidationError(
                    detail="Invalid source ID. Check the available ones at `/api/sources`, nyan!"
                )

        return [int(id) for id in ids]


class BooleanField(serializers.Field):
    def to_representation(self, value):
        return str(value).lower()

    def to_internal_value(self, data):
        if data is None:
            return None

        match data.lower():
            case "true":
                return True
            case "false":
                return False
            case "null":
                return None
            case _:
                raise serializers.ValidationError(
                    detail="Invalid boolean value. Check your input and try again, nyan!"
                )


class FloatField(serializers.Field):
    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        try:
            return float(data)
        except ValueError:
            raise serializers.ValidationError(
                detail="Invalid float value. Check your input and try again, nyan!"
            )


class IntegerField(serializers.Field):
    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        try:
            return int(data)
        except ValueError:
            raise serializers.ValidationError(
                detail="Invalid integer value. Check your input and try again, nyan!"
            )


class SearchQuerySerializer(serializers.Serializer):
    url = serializers.URLField(required=False)
    limit = IntegerField(
        default=10, validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    threshold = FloatField(
        validators=[MinValueValidator(1), MaxValueValidator(100)], required=False
    )
    sources = SourcesField(
        required=False,
        default=",".join([str(source["id"]) for source in registry["sources"]]),
    )
    nsfw = BooleanField(required=False)
