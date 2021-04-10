from __future__ import annotations

import random
import string
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models

from skole.models.base import SkoleManager, SkoleModel
from skole.utils.constants import Errors

if TYPE_CHECKING:  # pragma: no cover
    from skole.models.user import User


class InviteCodeManager(SkoleManager["InviteCode"]):
    def create_invite_code(self, user: User) -> InviteCode:
        if hasattr(user, "invite_code"):
            # Shouldn't ever happen in prod, but can happen on dev env when
            # verifying and unverifying a user multiple times.
            return user.invite_code

        invite_code = self.model(user=user)
        while True:
            invite_code.code = self._generate_code()
            try:
                invite_code.save()
            except IntegrityError:
                # The created code was miraculously non-unique.
                continue
            return invite_code

    @staticmethod
    def _generate_code() -> str:
        return "".join(
            random.choices(string.ascii_uppercase, k=settings.INVITE_CODE_LENGTH)
        )


class InviteCode(SkoleModel):
    """Models one invite code that a user can use to invite new users."""

    # Our physical codes cards are of length 8.
    code = models.CharField(max_length=max(8, settings.INVITE_CODE_LENGTH), unique=True)

    # The user that this code was created for and which they use to invite new users.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="invite_code",
    )

    usages = models.PositiveIntegerField(default=settings.INVITE_CODE_INITIAL_USAGES)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = InviteCodeManager()

    def __str__(self) -> str:
        return f"{self.user} - {self.code} - Usages: {self.usages}"

    def use_code(self, user: User) -> None:
        if user.used_invite_code:
            raise ValidationError(Errors.INVITE_CODE_ALREADY_SET)
        if self.usages <= 0:
            raise ValidationError(Errors.INVITE_CODE_NO_USES_LEFT)

        user.used_invite_code = self
        user.save(update_fields=("used_invite_code",))
        self.usages -= 1
        self.save(update_fields=("usages",))
