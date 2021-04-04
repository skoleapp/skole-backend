from __future__ import annotations

import random
import string
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models

from skole.models.base import SkoleManager, SkoleModel
from skole.utils.constants import GraphQLErrors, ValidationErrors

if TYPE_CHECKING:  # pragma: no cover
    from skole.models.user import User


class ReferralCodeManager(SkoleManager["ReferralCode"]):
    def create_referral_code(self, user: User) -> ReferralCode:
        referral_code = self.model(user=user)
        while True:
            referral_code.code = self._generate_code()
            try:
                referral_code.save()
            except IntegrityError:
                # The created code was miraculously non-unique.
                continue
            return referral_code

    @staticmethod
    def _generate_code() -> str:
        return "".join(
            random.choices(string.ascii_uppercase, k=settings.REFERRAL_CODE_LENGTH)
        )


class ReferralCode(SkoleModel):
    """Models one referral code that a user can use to invite new users."""

    # Our physical codes cards are of length 8.
    code = models.CharField(
        max_length=max(8, settings.REFERRAL_CODE_LENGTH), unique=True
    )

    # The user that this code was created for and which they use to invite new users.
    # A user can have more than one code possibly if we later decide to give out new ones.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="referral_codes",
    )

    usages = models.PositiveIntegerField(default=settings.REFERRAL_CODE_INITIAL_USAGES)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = ReferralCodeManager()

    def __str__(self) -> str:
        return f"{self.code} - Usages: {self.usages}"

    def use_code(self, user: User) -> None:
        if user.used_referral_code:
            raise ValidationError(GraphQLErrors.REFERRAL_CODE_ALREADY_SET)
        if self.usages <= 0:
            raise ValidationError(ValidationErrors.REFERRAL_CODE_NO_USES_LEFT)

        user.used_referral_code = self
        user.save(update_fields=("used_referral_code",))
        self.usages -= 1
        self.save(update_fields=("usages",))
