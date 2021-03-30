from django.utils.translation import gettext_lazy as _

from skole.utils.shortcuts import to_form_error as _m


class Admin:
    SITE_HEADER = _("Skole Administration")


class Languages:
    ENGLISH = _("English")
    FINNISH = _("Finnish")
    SWEDISH = _("Swedish")


class TokenAction:
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"


class ValidationErrors:
    USERNAME_TAKEN = _("This username is taken.")
    EMAIL_TAKEN = _("This email is taken.")
    EMAIL_DOES_NOT_EXIST = _("The email does not belong to an account.")
    EMAIL_DOMAIN_NOT_ALLOWED = _("The email address domain is not allowed.")
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
    COMMENT_EMPTY = _("Comment must include either text, an image or a file.")
    COMMENT_ONE_FILE = _("Comment can contain either an image or a file, but not both.")
    INVALID_USERNAME = _(
        "Usernames can only contain letters, numbers, and underscores."
    )
    COULD_NOT_CONVERT_FILE = _("File could not be converted to {} format.")
    VOTE_OWN_CONTENT = _("You cannot vote your own content.")
    REFERRAL_CODE_INVALID = _("The referral code does not seem to be valid.")
    REFERRAL_CODE_NO_USES_LEFT = _("The referral code does not have any uses left.")
    REFERRAL_CODE_NEEDED_BEFORE_LOGIN = _(
        "You need to use a referral code before you can log in."
    )
    INVALID_COMMENT_AUTHOR = _(
        "You cannot set someone else to be the author of your comment."
    )


class GraphQLErrors:
    INVALID_ORDERING = _("Invalid ordering value.")
    ALREADY_VERIFIED = _("This account has already been verified.")
    NOT_VERIFIED = _("This account is not verified.")
    TOKEN_SCOPE_ERROR = _("This token is not intended for this use.")
    UNSPECIFIED_ERROR = _("An error occurred. Trying again might help.")
    REFERRAL_CODE_NEEDED_BEFORE_VERIFY = _(
        "You need to use a referral code before validating your email."
    )
    REFERRAL_CODE_ALREADY_SET = _(
        "You have already activated your account with a referral code."
    )
    AUTH_REQUIRED = _("This action is only allowed for authenticated users.")
    VERIFICATION_REQUIRED = _(
        "This action is only allowed for users who have verified their accounts."
        " Please verify your account."
    )


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
    THREAD_CREATED = _("Thread created successfully!")
    THREAD_DELETED = _("Thread deleted successfully!")
    COMMENT_UPDATED = _("Comment updated successfully!")
    COMMENT_DELETED = _("Comment deleted successfully!")
    DATA_REQUEST_RECEIVED = _("Data request received successfully!")
    BADGE_TRACKING_CHANGED = _("Changed the tracked badge successfully!")
    REFERRAL_CODE_SUCCESS = _("Successfully used the referral code!")

    # Untranslated, these are strictly for development.
    FCM_TOKEN_UPDATED = "FCM token updated!"


class Notifications:
    MY_DATA_SUBJECT = "Your data request on Skole"
    VERIFY_ACCOUNT_SUBJECT = "Verify your account on Skole"
    RESET_PASSWORD_SUBJECT = "Reset your password on Skole"
    COMMUNITY_USER = "Community User"
    COMMENT_EMAIL_NOTIFICATION_SUBJECT = "{} {} in Skole"
    COMMENT_PUSH_NOTIFICATION_TITLE = "New Activity!"
    BADGE_EMAIL_NOTIFICATION_TITLE = "You Earned a New Badge in Skole"
    BADGE_PUSH_NOTIFICATION_TITLE = "New Badge!"
    BADGE_PUSH_NOTIFICATION_BODY = "Congratulations! You earned the '{}' badge."


class MutationErrors:
    # fmt: off
    NOT_OWNER = _m(ValidationErrors.NOT_OWNER)
    EMAIL_ERROR = _m(_("Error while sending email."))
    REGISTER_EMAIL_ERROR = _m(_(
        "Your account has been registered but we encountered"
        " an error while sending email. You may still log in using your credentials."
        " Please try verifying your account later."
    ))
    ALREADY_VERIFIED = _m(GraphQLErrors.ALREADY_VERIFIED)
    REFERRAL_CODE_NEEDED = _m(GraphQLErrors.REFERRAL_CODE_NEEDED_BEFORE_VERIFY)
    TOKEN_EXPIRED_VERIFY = _m(_("Token expired. Please request new verification link."))
    INVALID_TOKEN_VERIFY = _m(_("Invalid token. Please request new verification link."))
    BADGE_CANNOT_BE_NULL = _m(_("Invalid badge."))  # Should never be shown in frontend.
    USER_NOT_FOUND_WITH_EMAIL = _m(_(
        "User with the provided email was not found. Please check you email address."
    ))
    ACCOUNT_REMOVED = _m(_("This account has been removed."))
    TOKEN_EXPIRED_RESET_PASSWORD = _m(_(
        "Token expired. Please request new password reset link."
    ))
    INVALID_TOKEN_RESET_PASSWORD = _m(_(
        "Invalid token. Please request new password reset link."
    ))
    AUTH_REQUIRED = _m(GraphQLErrors.AUTH_REQUIRED)
    VERIFICATION_REQUIRED = _m(GraphQLErrors.VERIFICATION_REQUIRED)
    RATE_LIMITED = _m(_("You can request this next time in {} min."))
    # fmt: on


class VoteConstants:
    SCORE_THREAD_MULTIPLIER = 20
    SCORE_COMMENT_MULTIPLIER = 10

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
