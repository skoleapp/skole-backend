from __future__ import annotations

from typing import Optional, Union

from django.conf import settings
from django.db import models

from skole.models.base import SkoleManager, SkoleModel
from skole.models.resource import Resource
from skole.models.thread import Thread
from skole.models.user import User
from skole.types import StarrableModel


class StarManager(SkoleManager["Star"]):
    def create_or_delete_star(
        self, user: User, target: StarrableModel
    ) -> Optional[Star]:
        """Create a new star to the target or delete it if it already exists."""

        if isinstance(target, Thread):
            star = self.check_existing_star(user, thread=target)
        elif isinstance(target, Resource):
            star = self.check_existing_star(user, resource=target)
        else:
            raise TypeError(f"Invalid target type for Star: {type(target)}")

        return star

    def check_existing_star(
        self, user: User, **target: Union[Thread, Resource]
    ) -> Optional[Star]:
        try:
            star = user.stars.get(**target)
            star.delete()
            return None

        except Star.DoesNotExist:
            star = self.model(**target)
            star.user = user
            star.save()
            return star


class Star(SkoleModel):
    """Models a star that a user has placed on a thread or a resource."""

    _identifier_field = "user"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stars"
    )

    thread = models.ForeignKey(
        "skole.Thread",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stars",
    )

    resource = models.ForeignKey(
        "skole.Resource",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stars",
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = StarManager()

    class Meta:
        unique_together = ("user", "thread", "resource")

    def __str__(self) -> str:
        if self.thread is not None:
            return f"{self.user} - {self.thread}"
        elif self.resource is not None:
            return f"{self.user} - {self.resource}"
        else:
            raise ValueError("Invalid Star object.")
