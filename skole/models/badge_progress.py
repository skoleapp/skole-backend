import itertools
from collections.abc import Iterable
from typing import Optional

from django.conf import settings
from django.db import models
from django.utils import timezone

from .base import SkoleModel


class BadgeProgress(SkoleModel):
    """
    Models the progress of a single badge.

    E.g. User testuser2 can have a progress of 5/15 comments to get a 'Commenter' badge.
    """

    badge = models.ForeignKey(
        "skole.Badge", on_delete=models.CASCADE, related_name="badge_progresses"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="badge_progresses",
    )

    acquired = models.DateTimeField(default=None, null=True)
    progress = models.IntegerField(default=0)

    class Meta:
        unique_together = ("badge", "user")

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        if not self.acquired and self.badge.steps and self.progress >= self.badge.steps:
            self.acquired = timezone.now()
            self.user.change_score(self.badge.completion_score)

            if update_fields is not None and "progress" in update_fields:
                # `None` means to update all fields. If `update_fields` isn't `None` we anyways
                # want to to make sure `acquired` is saved here if `progress` is saved.
                update_fields = itertools.chain(update_fields, ("acquired",))

        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def __str__(self) -> str:
        if self.badge.steps:
            return f"{self.badge} ({self.progress}/{self.badge.steps}) - {self.user}"
        return f"{self.badge} ({'' if self.acquired else 'not '}acquired) - {self.user}"
