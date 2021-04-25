from __future__ import annotations

from typing import ClassVar

from skole.utils.constants import Errors


class _BaseGraphQLAuthError(Exception):
    message: ClassVar[str]

    def __init__(self) -> None:
        super().__init__(self.message)


class InviteCodeNeeded(_BaseGraphQLAuthError):
    message = Errors.INVITE_CODE_NEEDED_BEFORE_VERIFY


class UserAlreadyVerified(_BaseGraphQLAuthError):
    message = Errors.ALREADY_VERIFIED


class BackupEmailAlreadyVerified(_BaseGraphQLAuthError):
    message = Errors.BACKUP_EMAIL_ALREADY_VERIFIED


class UserNotVerified(_BaseGraphQLAuthError):
    message = Errors.NOT_VERIFIED


class TokenScopeError(_BaseGraphQLAuthError):
    message = Errors.TOKEN_SCOPE_ERROR
