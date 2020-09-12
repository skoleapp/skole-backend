from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse


class SkoleSessionMiddleware(SessionMiddleware):
    """
    Controls that JWT is used on the graphql endpoint and session auth on the admin.

    Reference: https://stackoverflow.com/a/4054339
    """

    def process_request(self, request: HttpRequest) -> None:
        if request.path == "/graphql/":
            # Disable session authentication on the graphql endpoint.

            # Ignore: The real type should be `SessionBase` instead of an empty dict,
            #   but this works just fine. The reason why we need this is
            #   that otherwise `AuthenticationMiddleware` complains
            #   that the request doesn't contain a session and thus it
            #   thinks no `SessionMiddleware` is installed.
            request.session = {}  # type: ignore[assignment]
        else:
            # Disable JWT authentication on the admin endpoint.
            request.COOKIES.pop("JWT", None)
            super().process_request(request)

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        if request.path == "/graphql/":
            return response
        return super().process_response(request, response)
