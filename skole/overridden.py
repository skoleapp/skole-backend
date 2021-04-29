from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, cast

import graphql_jwt.decorators
import graphql_jwt.exceptions
from django.http import HttpRequest

from skole.utils.constants import Errors

C = TypeVar("C", bound=Callable[..., Any])


def login_required(func: C) -> C:
    """
    Custom version of `graphql_jwt.decorators.login_required`, behavior is the same.

    This allows the wrapped function to know that it was wrapped with this decorator.
    This is used in `SkoleObjectTypeMeta` to dynamically add info to the API docs if
    logging in is required for that resolver.
    """

    @wraps(func)
    @graphql_jwt.decorators.context(func)
    def wrapper(context: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if context.user.is_authenticated:
            return func(*args, **kwargs)
        raise graphql_jwt.exceptions.PermissionDenied(Errors.AUTH_REQUIRED)

    setattr(wrapper, "login_required", True)
    return cast(C, wrapper)


def verification_required(func: C) -> C:
    """Use as a decorator on query resolver to make it require email verification."""

    @wraps(func)
    @graphql_jwt.decorators.context(func)
    @login_required
    def wrapper(context: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        # Ignore: `@login_required` makes sure that `user` cannot be anonymous.
        if context.user.verified:  # type: ignore[union-attr]
            return func(*args, **kwargs)
        raise graphql_jwt.exceptions.PermissionDenied(Errors.VERIFICATION_REQUIRED)

    setattr(wrapper, "verification_required", True)
    return cast(C, wrapper)
