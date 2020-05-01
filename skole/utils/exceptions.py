from skole.utils.constants import GraphQLErrors


class _BaseGraphQLAuthError(Exception):
    message: str

    def __init__(self) -> None:
        super().__init__(self.message)


class UserAlreadyVerified(_BaseGraphQLAuthError):
    message = GraphQLErrors.ALREADY_VERIFIED


class UserNotVerified(_BaseGraphQLAuthError):
    message = GraphQLErrors.NOT_VERIFIED


class TokenScopeError(_BaseGraphQLAuthError):
    message = GraphQLErrors.TOKEN_SCOPE_ERROR
