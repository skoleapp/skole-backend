from __future__ import annotations

from typing import Optional, Union

from django.conf import settings
from django.db import models

from skole.types import StarrableModel

from .base import SkoleManager, SkoleModel
from .course import Course
from .resource import Resource
from .user import User


class StarManager(SkoleManager["Star"]):
    def create_or_delete_star(
        self, user: User, target: StarrableModel
    ) -> Optional[Star]:
        """Create a new star to the target or delete it if it already exists."""

        if isinstance(target, Course):
            star = self.check_existing_star(user, course=target)
        elif isinstance(target, Resource):
            star = self.check_existing_star(user, resource=target)
        else:
            raise TypeError(f"Invalid target type for Star: {type(target)}")

        return star

    def check_existing_star(
        self, user: User, **target: Union[Course, Resource]
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
    """Models a star that a user has placed on a course or a resource."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stars"
    )

    course = models.ForeignKey(
        "skole.Course",
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

    objects = StarManager()

    class Meta:
        unique_together = ("user", "course", "resource")

    def __str__(self) -> str:
        if self.course is not None:
            return f"{self.user} - {self.course}"
        elif self.resource is not None:
            return f"{self.user} - {self.resource}"
        else:
            raise ValueError("Invalid star object.")
