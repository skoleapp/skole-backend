from functools import wraps
from typing import Any, Callable, TypeVar, cast

import graphql_jwt.decorators
import graphql_jwt.exceptions
from django.http import HttpRequest

Func = TypeVar("Func", bound=Callable[..., Any])


def login_required(func: Func) -> Func:
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
        raise graphql_jwt.exceptions.PermissionDenied

    setattr(wrapper, "login_required", True)
    return cast(Func, wrapper)