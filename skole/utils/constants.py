from django.utils.translation import gettext_lazy as _


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
    INVALID_BETA_CODE = _("Invalid beta code.")
    ACCOUNT_DEACTIVATED = _("This account has been deactivated!")
    AUTH_ERROR = _("Invalid username/email or password.")
    SUPERUSER_LOGIN = _("Cannot log in at this time.")
    INVALID_OLD_PASSWORD = _("Invalid old password.")
    INVALID_PASSWORD = _("Invalid password.")
    MUTATION_INVALID_TARGET = _("Mutation needs exactly one target.")
    NOT_OWNER = _("You are not the owner of this object.")
    FILE_TOO_LARGE = _("File is too large, maximum allowed is {} MB")
    INVALID_FILE_TYPE = _("Invalid file type, allowed types are: {}")


class GraphQLErrors:
    INVALID_ORDERING = _("Invalid ordering value.")
    ALREADY_VERIFIED = _("This account has already been verified.")
    NOT_VERIFIED = _("This account is not verified.")
    TOKEN_SCOPE_ERROR = _("This token is not intended for this use.")


class Messages:
    MESSAGE_SENT = _("Message sent successfully.")
    USER_REGISTERED = _("Registered new user successfully!")
    ACCOUNT_VERIFIED = _("Account verified successfully!")
    VERIFICATION_EMAIL_SENT = _("Verification link sent successfully!")
    PASSWORD_RESET_EMAIL_SENT = _("Password reset link sent successfully!")
    PASSWORD_UPDATED = _("Password updated successfully!")
    LOGGED_IN = _("Logged in successfully!")
    USER_DELETED = _("User deleted successfully!")
    USER_UPDATED = _("User details updated successfully!")
    COURSE_CREATED = _("Course created successfully!")
    COURSE_DELETED = _("Course deleted successfully!")
    RESOURCE_DELETED = _("Resource deleted successfully!")
    RESOURCE_CREATED = _("Resource created successfully!")
    RESOURCE_UPDATED = _("Resource updated successfully!")
    COMMENT_UPDATED = _("Comment updated successfully!")
    COMMENT_DELETED = _("Comment deleted successfully!")


class MutationErrors:
    COMMENT_EMPTY = [
        {
            "field": "__all__",
            "messages": [_("Comment must include either text or attachment.")],
        }
    ]
    NOT_OWNER = [{"field": "__all__", "messages": [ValidationErrors.NOT_OWNER],}]
    EMAIL_ERROR = [{"field": "__all__", "messages": [_("Error while sending email.")],}]
    ALREADY_VERIFIED = [
        {"field": "__all__", "messages": [GraphQLErrors.ALREADY_VERIFIED],}
    ]
    TOKEN_EXPIRED_VERIFY = [
        {
            "field": "__all__",
            "messages": [_("Token expired. Please request new verification link.")],
        }
    ]
    INVALID_TOKEN_VERIFY = [
        {
            "field": "__all__",
            "messages": [_("Invalid token. Please request new verification link.")],
        }
    ]
    USER_NOT_FOUND_WITH_EMAIL = [
        {
            "field": "__all__",
            "messages": [
                _(
                    "User with the provided email was not found. Please check you email address."
                )
            ],
        }
    ]
    NOT_VERIFIED_RESET_PASSWORD = [
        {
            "field": "__all__",
            "messages": [
                _(
                    "You must verify your account before resetting your password. A new verification email was sent. Please check your email."
                )
            ],
        }
    ]
    ACCOUNT_REMOVED = [
        {"field": "__all__", "messages": [_("This account has been removed.")],}
    ]
    TOKEN_EXPIRED_RESET_PASSWORD = [
        {
            "field": "__all__",
            "messages": [_("Token expired. Please request new password reset link.")],
        }
    ]
    INVALID_TOKEN_RESET_PASSWORD = [
        {
            "field": "__all__",
            "messages": [_("Invalid token. Please request new password reset link.")],
        }
    ]
    AUTH_REQUIRED = [
        {
            "field": "__all__",
            "messages": [_("This action is only allowed for authenticated users.")],
        }
    ]
    VERIFICATION_REQUIRED = [
        {
            "field": "__all__",
            "messages": [
                _(
                    "This action is only allowed for users who have verified their accounts. Please verify your account."
                )
            ],
        }
    ]
    VOTE_OWN_CONTENT = [
        {"field": "__all__", "messages": [_("You cannot vote your own content.")],}
    ]


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
    MASTER = _("Master")
    DOCTOR = _("Doctor")
    PROFESSOR = _("Professor")
