from typing import Optional

from skole.utils.constants import GraphQLErrors


class GraphQLAuthError(Exception):
    default_message: Optional[str] = None

    def __init__(self, message: Optional[str] = None) -> None:
        if message is None:
            message = self.default_message

        super().__init__(message)


class UserAlreadyVerified(GraphQLAuthError):
    default_message = GraphQLErrors.ALREADY_VERIFIED


class UserNotVerified(GraphQLAuthError):
    default_message = GraphQLErrors.NOT_VERIFIED


class TokenScopeError(GraphQLAuthError):
    default_message = GraphQLErrors.TOKEN_SCOPE_ERROR
