from rest_framework.views import APIView
from rest_framework.response import Response

from nekosauce.exceptions import NotFound, Forbidden, ServerInternalError


def error_400(request, exception):
    return Response(
        {
            "errors": [
                {
                    "status": "bad_request",
                    "message": "Seems like a value entered is not correct. Check your GET/POST params and try again!",
                    "code": 400,
                }
            ]
        },
        status=400,
    )


def error_403(request, exception):
    return Response(
        {
            "errors": [
                {
                    "status": "forbidden",
                    "message": "I got you! Are you sure you have permission to go there? Something is telling me you're not allowed... >:)",
                    "code": 403,
                },
            ]
        },
        status=403,
    )


def error_404(request, exception):
    return Response(
        {
            "errors": [
                {
                    "status": "not_found",
                    "message": "Welcome dev kitten! Looking for some sauces? Then you may want to read the docs at `https://docs.nekosauce.org/` :)",
                    "code": 404,
                },
            ],
        },
        status=404,
    )


def error_500(request):
    return Response(
        {
            "errors": [
                {
                    "status": "server_error",
                    "message": "Oopsie! Seems like something went wrong on our side :/ Maybe you want to report this error in our Discord server?",
                    "code": 500,
                }
            ],
        },
        status=500,
    )
