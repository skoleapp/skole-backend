import datetime
import importlib
import logging
from functools import update_wrapper
from traceback import format_exception
from types import TracebackType
from typing import Any, Optional, Union, cast

import graphql.execution.utils
import graphql_jwt.decorators
import graphql_jwt.utils
from django.conf import settings
from django.http import HttpResponse
from graphql_jwt.exceptions import PermissionDenied
from graphql_jwt.settings import jwt_settings

from skole.utils.constants import GraphQLErrors

logger = logging.getLogger(__name__)


def patch(obj: Any, value: Any) -> None:
    setattr(obj, value.__name__, update_wrapper(value, getattr(obj, value.__name__)))


def report_error(
    self: graphql.execution.utils.ExecutionContext,
    error: Exception,
    traceback: Optional[TracebackType] = None,
) -> None:
    """
    Patched to hide error details in prod.

    Also removes unnecessary 'permission denied' traceback spam from logs.
    """
    formatted_exception = format_exception(
        type(error), error, getattr(error, "stack", None) or traceback
    )
    if not isinstance(getattr(error, "original_error", error), PermissionDenied):
        logger.error("".join(formatted_exception))

        if not settings.DEBUG:  # pragma: no cover
            # Replace the detailed exception message with a more generic one.
            error.args = (GraphQLErrors.UNSPECIFIED_ERROR,)

    self.errors.append(error)


def set_cookie(
    response: HttpResponse,
    key: str,
    value: str,
    expires: Optional[Union[str, datetime.datetime]],
) -> None:
    """
    Patched to allow setting the `samesite` value for the cookie.

    This was already done in `django-graphql-jwt`
    it's just not yet released, thus the backport:
    https://github.com/flavors/django-graphql-jwt/commit/d26e9f856a7c41397561a2435a7fd75a19721e3c
    """
    response.set_cookie(
        key,
        value,
        expires=expires,
        httponly=True,
        secure=jwt_settings.JWT_COOKIE_SECURE,
        path=jwt_settings.JWT_COOKIE_PATH,
        domain=jwt_settings.JWT_COOKIE_DOMAIN,
        # Cannot access this from `jwt_settings` since it's not part of the
        # defaults yet and it would fail with on `AttributeError: Invalid setting`.
        samesite=cast(str, settings.GRAPHQL_JWT["JWT_COOKIE_SAMESITE"]),
    )


patch(graphql.execution.utils.ExecutionContext, report_error)

patch(graphql_jwt.utils, set_cookie)

# Since `set_cookie` was a top-level function, we need to reload the module
# that has already imported this.
importlib.reload(graphql_jwt.decorators)
