from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.db import models

from skole.models.base import SkoleManager, SkoleModel
from skole.models.thread import Thread
from skole.models.user import User


class StarManager(SkoleManager["Star"]):
    def create_or_delete_star(self, user: User, thread: Thread) -> Optional[Star]:
        """Create a new star to the target or delete it if it already exists."""
        try:
            star = user.stars.get(thread=thread)
            star.delete()
            return None
        except Star.DoesNotExist:
            star = self.model(thread=thread)
            star.user = user
            star.save()
            return star


class Star(SkoleModel):
    """Models a star that a user has placed on a thread."""

    _identifier_field = "user"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stars"
    )

    thread = models.ForeignKey(
        "skole.Thread",
        on_delete=models.CASCADE,
        related_name="stars",
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = StarManager()

    class Meta:
        unique_together = ("user", "thread")

    def __str__(self) -> str:
        return f"{self.user} - {self.thread}"
