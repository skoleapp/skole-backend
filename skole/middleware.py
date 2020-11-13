"""This module contains all the Django and GraphQL middlewares used in the app."""
from typing import Any, Callable, Optional, TypeVar

from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse

from skole.types import ResolveInfo


class SkoleSessionMiddleware(SessionMiddleware):
    """
    Controls that JWT is used on the GraphQL endpoint and session auth on the admin.

    References: https://stackoverflow.com/a/4054339/9835872
    """

    def process_request(self, request: HttpRequest) -> None:
        if request.path == "/graphql/":
            # Disable session authentication on the GraphQL endpoint.

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


T = TypeVar("T")


class DisableIntrospectionMiddleware:
    """
    GraphQL middleware that disables schema introspection.

    This is used in production (when DEBUG is False).

    If a client queries a disallowed field, this will return GraphQL errors like:
    `"Cannot return null for non-nullable field Query.__schema."`, but it should be
    fine, since the error only shows up on the client and not as traceback in logs.

    References:
        https://medium.com/@pkinuthia10/disabling-djanog-graphene-introspection-query-8042b341c675
        https://lab.wallarm.com/why-and-how-to-disable-introspection-query-for-graphql-apis/
    """

    def resolve(
        self, next: Callable[..., T], root: Any, info: ResolveInfo, **kwargs: Any
    ) -> Optional[T]:
        if info.field_name.startswith("_") and info.field_name != "__typename":
            # Apollo client queries `__typename` with every request
            # and uses it for caching, so we special case it here.
            return None
        return next(root, info, **kwargs)
