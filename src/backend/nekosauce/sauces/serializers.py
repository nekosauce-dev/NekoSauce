from rest_framework import serializers
from django.core.validators import MinValueValidator


class SearchQuerySerializer(serializers.Serializer):
    url = serializers.URLField(required=False)
    algorithm = serializers.ChoiceField(
        choices=(
            (0, "perceptual"),
            (1, "average"),
            (3, "diferential"),
            (4, "wavelet"),
        ),
        required=True,
    )
    bits = serializers.ChoiceField(choices=(8, 16, 32, 64), required=True)
    limit = serializers.IntegerField(default=10, validators=[MinValueValidator(1)])
