from typing import Optional

from skole.utils.constants import GraphQLErrors


class GraphQLAuthError(Exception):
    default_message = None

    def __init__(self, message: Optional[str] = None) -> None:
        if message is None:
            message = self.default_message

        super().__init__(message)


class UserAlreadyVerified(GraphQLAuthError):
    # Ignore: Mypy expects a `None` type default message
    default_message = GraphQLErrors.ALREADY_VERIFIED  # type: ignore [assignment]


class UserNotVerified(GraphQLAuthError):
    # Ignore: Mypy expects a `None` type default message
    default_message = GraphQLErrors.NOT_VERIFIED  # type: ignore [assignment]


class TokenScopeError(GraphQLAuthError):
    # Ignore: Mypy expects a `None` type default message
    default_message = GraphQLErrors.TOKEN_SCOPE_ERROR  # type: ignore [assignment]
