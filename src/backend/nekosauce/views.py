from rest_framework.views import APIView
from rest_framework.response import Response

from nekosauce.exceptions import NotFound, Forbidden, ServerInternalError


def error_400(request, exception):
    raise ValidationError(
        "Seems like a value entered is not correct. Check your GET/POST params and try again!"
    )


def error_403(request, exception):
    raise Forbidden(
        "I got you! Are you sure you have permission to go there? Something is telling me you're not allowed... >:)"
    )


def error_404(request, exception):
    raise NotFound(
        "Welcome dev kitten! Looking for some sauces? Then you may want to read the docs at `https://docs.nekosauce.org/` :)"
    )


def error_500(request, exception):
    raise ServerInternalError(
        "Oopsie! Seems like something went wrong on our side :/ Maybe you want to report this error in our Discord server?"
    )
