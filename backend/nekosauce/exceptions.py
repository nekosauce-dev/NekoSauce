from rest_framework.views import exception_handler as default_exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException


class ValidationError(APIException):
    default_code = "validation_error"
    default_detail = "Seems like a value entered is not correct. Check your GET/POST params and try again!"
    status_code = 400


class DownloadError(APIException):
    default_code = "download_error"
    default_detail = "Oops! Something went wrong while downloading the file."
    status_code = 400


def exception_handler(exc, context):
    if isinstance(exc, APIException):
        return Response(
            {
                "errors": [
                    {
                        "status": exc.default_code,
                        "message": exc.detail,
                        "code": exc.status_code,
                    }
                ]
            },
            status=exc.status_code,
        )

    return default_exception_handler(exc, context)
