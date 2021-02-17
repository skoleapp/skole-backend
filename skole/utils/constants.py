from typing import Any, TypeVar, cast

from django.utils.translation import gettext_lazy as _

from skole.types import FormError


class Admin:
    SITE_HEADER = _("Skole Administration")


class Languages:
    ENGLISH = _("English")
    FINNISH = _("Finnish")
    SWEDISH = _("Swedish")


class TokenAction:
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    UPDATE_EMAIL_SUBSCRIPTION = "update-email-subscription"


class ValidationErrors:
    USERNAME_TAKEN = _("This username is taken.")
    EMAIL_TAKEN = _("This email is taken.")
    EMAIL_ALREADY_SUBSCRIBED = _("A subscription with this email already exists.")
    ACCOUNT_EMAIL = _(
        "This email belongs to an account. You can edit your email preferences in your account settings."
    )
    ACCOUNT_DEACTIVATED = _("This account has been deactivated!")
    AUTH_ERROR = _("Invalid username/email or password.")
    SUPERUSER_LOGIN = _("Cannot log in at this time.")
    INVALID_OLD_PASSWORD = _("Invalid old password.")
    INVALID_PASSWORD = _("Invalid password.")
    MUTATION_INVALID_TARGET = _("Mutation needs exactly one target.")
    NOT_OWNER = _("You are not the owner of this object.")
    FILE_TOO_LARGE = _("File is too large, maximum allowed is {} MB")
    INVALID_FILE_TYPE = _("Invalid file type, allowed types are: {}")
    INVALID_FILE_EXTENSION = _("File extension doesn't match the file type.")
    COMMENT_EMPTY = _("Comment must include either text or attachment.")
    INVALID_USERNAME = _(
        "Usernames can only contain letters, numbers, and underscores."
    )
    COULD_NOT_CONVERT_FILE = _("File could not be converted to {} format.")
    VOTE_OWN_CONTENT = _("You cannot vote your own content.")
    COURSE_CODE_INVALID = _("One of the course codes is invalid.")


class GraphQLErrors:
    INVALID_ORDERING = _("Invalid ordering value.")
    ALREADY_VERIFIED = _("This account has already been verified.")
    NOT_VERIFIED = _("This account is not verified.")
    TOKEN_SCOPE_ERROR = _("This token is not intended for this use.")
    UNSPECIFIED_ERROR = _("An error occurred. Trying again might help.")


class Messages:
    MESSAGE_SENT = _("Message sent successfully.")
    USER_REGISTERED = _("Registered new user successfully!")
    ACCOUNT_VERIFIED = _("Account verified successfully!")
    VERIFICATION_EMAIL_SENT = _("Verification link sent successfully!")
    PASSWORD_RESET_EMAIL_SENT = _("Password reset link sent successfully!")
    PASSWORD_UPDATED = _("Password updated successfully!")
    LOGGED_IN = _("Logged in successfully!")
    USER_DELETED = _("Account deleted successfully!")
    PROFILE_UPDATED = _("Profile updated successfully!")
    ACCOUNT_SETTINGS_UPDATED = _("Account settings updated successfully!")
    COURSE_CREATED = _("Course created successfully!")
    COURSE_DELETED = _("Course deleted successfully!")
    RESOURCE_DELETED = _("Resource deleted successfully!")
    RESOURCE_CREATED = _("Resource created successfully!")
    RESOURCE_UPDATED = _("Resource updated successfully!")
    RESOURCE_DOWNLOADS_UPDATED = _("Resource downloads updated!")
    COMMENT_UPDATED = _("Comment updated successfully!")
    COMMENT_DELETED = _("Comment deleted successfully!")
    DATA_REQUEST_RECEIVED = _("Data request received successfully!")
    SUBSCRIBED = _("Subscribed successfully!")
    SUBSCRIPTION_UPDATED = _("Subscription updated successfully!")
    SUBSCRIPTION_DELETED = _("Subscription deleted successfully!")


class Email:
    MY_DATA_SUBJECT = _("Your data request on Skole")
    VERIFY_ACCOUNT_SUBJECT = _("Verify your account on Skole")
    RESET_PASSWORD_SUBJECT = _("Reset your password on Skole")


T = TypeVar("T", bound="_MutationErrorsMeta")


class _MutationErrorsMeta(type):
    def __new__(
        mcs: type[T], name: str, bases: tuple[type, ...], attrs: dict[str, Any]
    ) -> T:
        """Add the GraphQL form error structure for all class attributes."""
        for key, value in attrs.items():
            if not (key.startswith("__") and key.endswith("__")):
                # Don't want to affect __magic__ attrs.
                attrs[key] = [{"field": "__all__", "messages": [value]}]
        return cast(T, super().__new__(mcs, name, bases, attrs))


def _c(field: str) -> FormError:
    """Used to cast all `MutationErrors` fields to the type that the metaclass makes."""
    return cast(FormError, field)


class MutationErrors(metaclass=_MutationErrorsMeta):
    # fmt: off
    NOT_OWNER = _c(ValidationErrors.NOT_OWNER)
    EMAIL_ERROR = _c(_("Error while sending email."))
    REGISTER_EMAIL_ERROR = _c(_(
        "Your account has been registered but we encountered"
        " an error while sending email. You may still log in using your credentials."
        " Please try verifying your account later."
    ))
    ALREADY_VERIFIED = _c(GraphQLErrors.ALREADY_VERIFIED)
    TOKEN_EXPIRED_VERIFY = _c(_("Token expired. Please request new verification link."))
    INVALID_TOKEN_VERIFY = _c(_("Invalid token. Please request new verification link."))
    INVALID_TOKEN = _c(_("Invalid token."))
    USER_NOT_FOUND_WITH_EMAIL = _c(_(
        "User with the provided email was not found. Please check you email address."
    ))
    ACCOUNT_REMOVED = _c(_("This account has been removed."))
    TOKEN_EXPIRED_RESET_PASSWORD = _c(_(
        "Token expired. Please request new password reset link."
    ))
    INVALID_TOKEN_RESET_PASSWORD = _c(_(
        "Invalid token. Please request new password reset link."
    ))
    AUTH_REQUIRED = _c(_("This action is only allowed for authenticated users."))
    VERIFICATION_REQUIRED = _c(_(
        "This action is only allowed for users who have verified their accounts."
        " Please verify your account."
    ))
    RATE_LIMITED = _c(_("You can request this next time in {} min."))
    # fmt: on


class VoteConstants:
    SCORE_RESOURCE_MULTIPLIER = 10
    SCORE_COURSE_MULTIPLIER = 5
    SCORE_COMMENT_MULTIPLIER = 1

    STATUS = (
        (1, "upvote"),
        (-1, "downvote"),
    )


class Ranks:
    FRESHMAN = _("Freshman")
    TUTOR = _("Tutor")
    MENTOR = _("Mentor")
    BACHELOR = _("Bachelor")
    MASTER = _("Master")
    DOCTOR = _("Doctor")
    PROFESSOR = _("Professor")


class ActivityTypes:
    """Used in activity signal to get the correct activity type from the fixtures."""

    COMMENT_REPLY = "comment_reply"
    COURSE_COMMENT = "course_comment"
    RESOURCE_COMMENT = "resource_comment"


class VerboseNames:
    USERNAME = _("username")
    EMAIL = _("email")


DJANGO_STANDARD_MESSAGES_TO_OVERRIDE = [
    _("The password is too similar to the %(verbose_name)s.")
]


class MarketingEmailTypes:
    PRODUCT_UPDATE = "product-update"
    BLOG_POST = "blog-post"


MARKETING_EMAIL_TYPE_CHOICES = (
    (MarketingEmailTypes.PRODUCT_UPDATE, "Product Update"),
    (MarketingEmailTypes.BLOG_POST, "Blog Post"),
)
