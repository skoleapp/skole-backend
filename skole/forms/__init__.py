from __future__ import annotations

from .activity import MarkActivityAsReadForm
from .comment import CreateCommentForm, DeleteCommentForm, UpdateCommentForm
from .contact import ContactForm
from .star import CreateStarForm
from .thread import CreateThreadForm, DeleteThreadForm
from .user import (
    ChangePasswordForm,
    DeleteUserForm,
    EmailForm,
    InviteCodeForm,
    LoginForm,
    RegisterForm,
    SetPasswordForm,
    TokenForm,
    UpdateAccountSettingsForm,
    UpdateProfileForm,
    UpdateSelectedBadgeForm,
)
from .vote import CreateVoteForm

__all__ = [
    "ChangePasswordForm",
    "ContactForm",
    "CreateCommentForm",
    "CreateThreadForm",
    "CreateStarForm",
    "CreateVoteForm",
    "DeleteCommentForm",
    "DeleteThreadForm",
    "DeleteUserForm",
    "EmailForm",
    "LoginForm",
    "MarkActivityAsReadForm",
    "InviteCodeForm",
    "RegisterForm",
    "SetPasswordForm",
    "TokenForm",
    "UpdateAccountSettingsForm",
    "UpdateCommentForm",
    "UpdateProfileForm",
    "UpdateSelectedBadgeForm",
]
