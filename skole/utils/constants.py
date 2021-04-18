import re
from typing import Any

from django.utils.translation import gettext_lazy as _

from skole.utils.shortcuts import to_form_error


class Admin:
    SITE_HEADER = _("Skole Administration")


class Languages:
    ENGLISH = _("English")
    FINNISH = _("Finnish")
    SWEDISH = _("Swedish")


class TokenAction:
    VERIFICATION = "verification"
    BACKUP_EMAIL_VERIFICATION = "backup_email_verification"
    PASSWORD_RESET = "password_reset"


class Errors:
    ACCOUNT_DEACTIVATED = _("This account has been deactivated!")
    ACCOUNT_REMOVED = _("This account has been removed.")
    ALREADY_VERIFIED = _("This account has already been verified.")
    AUTH_ERROR = _("Invalid username/email or password.")
    AUTH_REQUIRED = _("This action is only allowed for authenticated users.")
    BACKUP_EMAIL_ALREADY_VERIFIED = _("Your backup email is already verified.")
    BACKUP_EMAIL_NOT_SAME_AS_EMAIL = _(
        "Your backup email cannot be the same as your primary email."
    )
    BADGE_CANNOT_BE_NULL = _("Invalid badge.")  # Should never be shown in frontend.
    COMMENT_EMPTY = _("Comment must include either text, an image or a file.")
    COMMENT_ONE_FILE = _("Comment can contain either an image or a file, but not both.")
    COULD_NOT_CONVERT_FILE = _("File could not be converted to {} format.")
    EMAIL_DOMAIN_NOT_ALLOWED = _("The email address domain is not allowed.")
    EMAIL_ERROR = _("Error while sending email.")
    EMAIL_TAKEN = _("This email is taken.")
    FILE_TOO_LARGE = _("File is too large, maximum allowed is {} MB")
    INVALID_COMMENT_AUTHOR = _(
        "You cannot set someone else to be the author of your comment."
    )
    INVALID_FILE_EXTENSION = _("File extension doesn't match the file type.")
    INVALID_FILE_TYPE = _("Invalid file type, allowed types are: {}")
    INVALID_OLD_PASSWORD = _("Invalid old password.")
    INVALID_ORDERING = _("Invalid ordering value.")
    INVALID_PASSWORD = _("Invalid password.")
    INVALID_TOKEN_RESET_PASSWORD = _(
        "Invalid token. Please request new password reset link."
    )
    INVALID_TOKEN_VERIFY = _("Invalid token. Please request new verification link.")
    INVALID_USERNAME = _(
        "Usernames can only contain letters, numbers, and underscores."
    )
    MUTATION_INVALID_TARGET = _("Mutation needs exactly one target.")
    NOT_OWNER = _("You are not the owner of this object.")
    NOT_VERIFIED = _("This account is not verified.")
    RATE_LIMITED = _("You can request this next time in {} min.")
    INVITE_CODE_ALREADY_SET = _(
        "You have already activated your account with a invite code."
    )
    INVITE_CODE_INVALID = _("The invite code does not seem to be valid.")
    INVITE_CODE_NEEDED_BEFORE_LOGIN = _(
        "You need to use an invite code before you can log in."
    )
    INVITE_CODE_NEEDED_BEFORE_VERIFY = _(
        "You need to use an invite code before validating your email."
    )
    INVITE_CODE_NO_USES_LEFT = _("The invite code does not have any uses left.")
    INVITE_CODE_VERIFIED = _("Verified users cannot use invite codes.")
    REGISTER_EMAIL_ERROR = _(
        "Your account has been registered but we encountered an error while sending "
        "email. You may still log in using your credentials. "
        "Please try verifying your account later."
    )
    SUPERUSER_LOGIN = _("Cannot log in at this time.")
    TOKEN_EXPIRED_RESET_PASSWORD = _(
        "Token expired. Please request new password reset link."
    )
    TOKEN_EXPIRED_VERIFY = _("Token expired. Please request new verification link.")
    TOKEN_SCOPE_ERROR = _("This token is not intended for this use.")
    UNSPECIFIED_ERROR = _("An error occurred. Trying again might help.")
    USERNAME_TAKEN = _("This username is taken.")
    USER_NOT_FOUND_WITH_EMAIL = _(
        "User with the provided email was not found. Please check you email address."
    )
    VERIFICATION_REQUIRED = _(
        "This action is only allowed for users who have verified their accounts. "
        "Please verify your account."
    )
    VOTE_OWN_CONTENT = _("You cannot vote your own content.")


class Messages:
    ACCOUNT_SETTINGS_UPDATED = _("Account settings updated successfully!")
    ACCOUNT_VERIFIED = _("Account verified successfully!")
    BACKUP_EMAIL_VERIFIED = _("Backup email verified successfully!")
    BADGE_TRACKING_CHANGED = _("Changed the tracked badge successfully!")
    COMMENT_DELETED = _("Comment deleted successfully!")
    COMMENT_UPDATED = _("Comment updated successfully!")
    DATA_REQUEST_RECEIVED = _("Data request received successfully!")
    LOGGED_IN = _("Logged in successfully!")
    MESSAGE_SENT = _("Message sent successfully.")
    PASSWORD_RESET_EMAIL_SENT = _("Password reset link sent successfully!")
    PASSWORD_UPDATED = _("Password updated successfully!")
    PROFILE_UPDATED = _("Profile updated successfully!")
    INVITE_CODE_SUCCESS = _("Successfully used the invite code!")
    THREAD_CREATED = _("Thread created successfully!")
    THREAD_DELETED = _("Thread deleted successfully!")
    USER_DELETED = _("Account deleted successfully!")
    USER_REGISTERED = _("Registered new user successfully!")
    VERIFICATION_EMAIL_SENT = _("Verification link sent successfully!")

    # Untranslated, these are strictly for development.
    FCM_TOKEN_UPDATED = "FCM token updated!"


class Notifications:
    BADGE_EMAIL_NOTIFICATION_TITLE = "You Earned a New Badge in Skole"
    BADGE_PUSH_NOTIFICATION_BODY = "Congratulations! You earned the '{}' badge."
    BADGE_PUSH_NOTIFICATION_TITLE = "New Badge!"
    COMMENT_EMAIL_NOTIFICATION_SUBJECT = "{} {} in Skole"
    COMMENT_PUSH_NOTIFICATION_TITLE = "New Activity!"
    ANONYMOUS_STUDENT = "Anonymous Student"
    MY_DATA_SUBJECT = "Your data request on Skole"
    RESET_PASSWORD_SUBJECT = "Reset your password on Skole"
    VERIFY_ACCOUNT_SUBJECT = "Verify your account on Skole"
    VERIFY_BACKUP_EMAIL_SUBJECT = "A backup email was added to your account on Skole"


class _MutationErrorsMeta(type):
    def __getattribute__(cls, name: str) -> Any:
        value = type.__getattribute__(cls, name)
        if re.match(r"^[A-Z_]+$", name):
            return to_form_error(value)
        return value


class MutationErrors(Errors, metaclass=_MutationErrorsMeta):
    """
    Contains all the same attributes as `Errors` class does.

    The difference is that accessing them from this wraps them in the graphene form
    mutation error structure.

    Examples:
        >>> Errors.BADGE_CANNOT_BE_NULL
        'Invalid badge.'
        >>> MutationErrors.BADGE_CANNOT_BE_NULL
        [{'field': '__all__', 'messages': ['Invalid badge.']}]

    Notes:
        This inherits `Errors`, even though the metaclass could manage fine without it,
        so that IDE autocompletion conveniently suggests its attributes.
    """


class VoteConstants:
    SCORE_COMMENT_MULTIPLIER = 10
    SCORE_THREAD_MULTIPLIER = 20

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
    THREAD_COMMENT = "thread_comment"
    NEW_BADGE = "new_badge"


class VerboseNames:
    USERNAME = _("username")
    EMAIL = _("email")


DJANGO_STANDARD_MESSAGES_TO_OVERRIDE = [
    _("The password is too similar to the %(verbose_name)s.")
]

# Keep these untranslated, and return the non-display value to frontend
# as a GraphQL Enum type. It makes conditional rendering easier there.
BADGE_TIER_CHOICES = (
    ("diamond", "Diamond"),
    ("gold", "Gold"),
    ("silver", "Silver"),
    ("bronze", "Bronze"),
)
