from rest_framework.views import APIView
from rest_framework.response import Response

from nekosauce.exceptions import NotFound


class IndexView(APIView):
    def get(self, request):
        raise NotFound(
            "Welcome dev kitten! Looking for some sauces? Then you may want to read the docs at `https://docs.nekosauce.org/` :)"
        )
