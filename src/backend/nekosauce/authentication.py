import re

from rest_framework import authentication
from rest_framework import exceptions

from nekosauce.users.models import User


class ApiKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return None

        prog = re.compile(r"^ApiKey (?P<api_key>[a-zA-Z0-9_-]{86})$")
        if not prog.fullmatch(authorization_header):
            raise exceptions.AuthenticationFailed(
                "The header's value is invalid. Check it again, nya!",
                code="invalid_header",
            )

        api_key = list(prog.finditer(authorization_header))[0].groupdict()["api_key"]

        try:
            user = User.objects.get(api_key=api_key)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                "Is that a valid API key, nyan? I cannot find anyone with that key!",
                code="invalid_api_key",
            )

        return (user, None)
