from __future__ import annotations

from django.db import models

from skole.models.base import SkoleModel


class AttemptedEmail(SkoleModel):
    """
    Models an email that was attempted to register with but wasn't allowed.

    We currently have a very limited amount of domains in `ALLOWED_EMAIL_DOMAINS`, but
    if one would try to register with a disallowed domain we could check it case by case
    and 'is_whitelisted' the address + inform the user via email that they were let in.

    This can also give us indication of which email domains we should add to
    `ALLOWED_EMAIL_DOMAINS`, since we could have easily forgot some important ones
    from there.
    """

    _identifier_field = "email"

    email = models.EmailField(unique=True)

    # The amount of times that this email address has been tried [unsuccessfully]
    # to be used for registration. Can be useful to see who are the most eager ones.
    attempts = models.PositiveIntegerField(default=0)

    # Whether this exact specific email address has been whitelisted (from admin panel)
    # to be allowed to be used for registration.
    is_whitelisted = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return (
            f"{self.email}, attempts: {self.attempts}, "
            f"{'' if self.is_whitelisted else 'not '}whitelisted"
        )
