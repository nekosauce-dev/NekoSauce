import json

from django.http.response import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response

from nekosauce.exceptions import NotFound, Forbidden, ServerInternalError


def error_400(request, exception):
    return HttpResponse(
        json.dumps(
            {
                "errors": [
                    {
                        "status": "bad_request",
                        "message": "Seems like a value entered is not correct. Check your GET/POST params and try again!",
                        "code": 400,
                    }
                ]
            }
        ),
        status=400,
    )


def error_403(request, exception):
    return HttpResponse(
        json.dumps(
            {
                "errors": [
                    {
                        "status": "forbidden",
                        "message": "Oopsie! Seems like u r not allowed in here :/ Go get more power in Rise of Kingdoms and try again later >:)",
                        "code": 403,
                    },
                ]
            }
        ),
        status=403,
    )


def error_404(request, exception):
    return HttpResponse(
        json.dumps(
            {
                "errors": [
                    {
                        "status": "not_found",
                        "message": "Not found, nya! U sure it was here? >.<",
                        "code": 404,
                    },
                ],
            }
        ),
        status=404,
    )


def error_500(request):
    return HttpResponse(
        json.dumps(
            {
                "errors": [
                    {
                        "status": "internal_server_error",
                        "message": "Looks like the sauce searching catgirl broke something :/ Try again later, nyan!",
                        "code": 500,
                    }
                ],
            }
        ),
        status=500,
    )


def index(request):
    return HttpResponse(
        json.dumps(
            {
                "errors": [
                    {
                        "status": "not_found",
                        "message": "Welcome dev kitten! Looking for some sauces? Then you may want to read the docs at `https://docs.nekosauce.org/` :)",
                        "code": 404,
                    },
                ],
            }
        ),
        status=404,
    )