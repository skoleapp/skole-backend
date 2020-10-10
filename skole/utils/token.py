from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, Union

from django.core import signing
from graphql_jwt.exceptions import JSONWebTokenError

from skole.types import JsonDict
from skole.utils.exceptions import TokenScopeError

if TYPE_CHECKING:  # pragma: no cover
    # To avoid circular import.
    from skole.models import User


def get_token(user: User, action: str, **kwargs: Any) -> str:
    username = user.get_username()

    payload = {"username": username, "action": action}

    if kwargs:
        payload.update(**kwargs)

    token = signing.dumps(payload)
    return token


def revoke_user_refresh_tokens(user: User) -> None:
    # Ignore: Mypy doesn't pick up the `refresh_tokens` relation from `graphql_jwt`.
    refresh_tokens = user.refresh_tokens.all()  # type: ignore

    for refresh_token in refresh_tokens:
        try:
            refresh_token.revoke()
        except JSONWebTokenError:
            pass


def get_token_payload(
    token: str, action: str, exp: Union[int, timedelta, None] = None
) -> JsonDict:
    payload = signing.loads(token, max_age=exp)
    _action = payload.pop("action")

    if _action != action:
        raise TokenScopeError

    return payload
