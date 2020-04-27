from datetime import timedelta
from typing import TYPE_CHECKING, Any, Union

from django.core import signing
from mypy.types import JsonDict

from skole.utils.exceptions import TokenScopeError

if TYPE_CHECKING:
    from skole.models import User


def get_token(user: "User", action: str, **kwargs: Any) -> str:
    username = user.get_username()

    if hasattr(username, "pk"):
        # Ignore: Some weird shit: https://github.com/flavors/django-graphql-jwt/blob/master/graphql_jwt/utils.py#L17
        username = username.pk  # type: ignore [attr-defined]

    payload = {"username": username, "action": action}

    if kwargs:
        payload.update(**kwargs)

    token = signing.dumps(payload)
    return token


def revoke_user_refresh_tokens(user: "User") -> None:
    # Ignore: Mypy doesn't pick up the `refresh_tokens` relation from `graphql_jwt`.
    refresh_tokens = user.refresh_tokens.all()  # type: ignore

    for refresh_token in refresh_tokens:
        try:
            refresh_token.revoke()
        except Exception:  # JSONWebTokenError
            pass


def get_token_payload(
    token: str, action: str, exp: Union[int, timedelta, None] = None
) -> JsonDict:
    payload = signing.loads(token, max_age=exp)
    _action = payload.pop("action")

    if _action != action:
        raise TokenScopeError

    return payload