from django.utils.translation import gettext_lazy as _

AUTH_ERROR_MESSAGE = _("Invalid username or password.")
NOT_OWNER_MESSAGE = _("You are not the owner of this object.")
EMAIL_ERROR_MESSAGE = _("Error while sending email.")  # TODO: Translate this.

ACCOUNT_ALREADY_VERIFIED_MESSAGE = _(
    "This account has already been verified."
)  # TODO: Translate this.

USER_NOT_FOUND_WITH_PROVIDED_EMAIL_MESSAGE = _(
    "A user with the provided email was not found."
)  # TODO: Translate this.
