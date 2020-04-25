from datetime import timedelta
from typing import Any, Union

from django.core import signing
from mypy.types import JsonDict

from skole.utils.exceptions import TokenScopeError


# Ignore: `User` model cannot be imported due to circular import or `AUTH_USER_MODEL` not being defined.
def get_token(user: "User", action: str, **kwargs: Any) -> str:  # type: ignore [name-defined]
    username = user.username

    if hasattr(username, "pk"):
        username = username.pk

    payload = {"username": username, "action": action}

    if kwargs:
        payload.update(**kwargs)

    token = signing.dumps(payload)
    return token


# Ignore: same as above.
def revoke_user_refresh_tokens(user: "User") -> None:  # type: ignore [name-defined]
    refresh_tokens = user.refresh_tokens.all()

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
