from .activity import MarkActivityAsReadForm
from .comment import CreateCommentForm, DeleteCommentForm, UpdateCommentForm
from .contact import ContactForm
from .course import CreateCourseForm, DeleteCourseForm
from .email_subscription import CreateEmailSubscriptionForm, UpdateEmailSubscriptionForm
from .resource import (
    CreateResourceForm,
    DeleteResourceForm,
    DownloadResourceForm,
    UpdateResourceForm,
)
from .star import CreateStarForm
from .user import (
    ChangePasswordForm,
    DeleteUserForm,
    EmailForm,
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
    "CreateCourseForm",
    "CreateEmailSubscriptionForm",
    "CreateResourceForm",
    "CreateStarForm",
    "CreateVoteForm",
    "DeleteCommentForm",
    "DeleteCourseForm",
    "DeleteResourceForm",
    "DeleteUserForm",
    "DownloadResourceForm",
    "EmailForm",
    "LoginForm",
    "MarkActivityAsReadForm",
    "RegisterForm",
    "SetPasswordForm",
    "TokenForm",
    "UpdateAccountSettingsForm",
    "UpdateCommentForm",
    "UpdateEmailSubscriptionForm",
    "UpdateProfileForm",
    "UpdateSelectedBadgeForm",
    "UpdateResourceForm",
]
