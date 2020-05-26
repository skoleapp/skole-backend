from typing import Any, Optional

from django.core.handlers.wsgi import WSGIRequest
from graphql_jwt.backends import JSONWebTokenBackend
from graphql_jwt.exceptions import JSONWebTokenError
from graphql_jwt.shortcuts import get_user_by_token
from graphql_jwt.utils import get_credentials


class SkoleAuthBackend(JSONWebTokenBackend):
    """Only difference from the original `JSONWebTokenBackend` is that it does not raise
    error when `get_user_by_token` fails.

    Main advantage is to let the mutation handle the authentication error. Instead of
    raising GraphQL errors with ugly tracebacks we can return form error messages etc.
    """

    def authenticate(
        self, request: Optional[WSGIRequest] = None, **kwargs: Any
    ) -> None:
        if request is None or getattr(request, "_jwt_token_auth", False):
            return None

        token = get_credentials(request, **kwargs)

        try:
            if token is not None:
                return get_user_by_token(token, request)
        except JSONWebTokenError:
            pass

        return None
