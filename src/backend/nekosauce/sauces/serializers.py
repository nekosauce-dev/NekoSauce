from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator


class SearchQuerySerializer(serializers.Serializer):
    url = serializers.URLField(required=False)
    limit = serializers.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(50)])
