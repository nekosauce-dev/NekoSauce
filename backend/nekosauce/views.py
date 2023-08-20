from rest_framework.views import APIView
from rest_framework.response import Response


class IndexView(APIView):
    def get(self, request):
        return Response(
            {
                "errors": [
                    {
                        "message": "Welcome dev kitten! Looking for some sauces? Then you may want to read the docs at `https://nekosauce.org/docs` :)",
                        "status": "not_found",
                        "code": 404,
                    }
                ]
            },
            status=404,
        )
