from .activity import MarkActivityAsReadForm
from .comment import CreateCommentForm, DeleteCommentForm, UpdateCommentForm
from .contact import ContactForm
from .course import CreateCourseForm, DeleteCourseForm
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
)
from .vote import CreateVoteForm
