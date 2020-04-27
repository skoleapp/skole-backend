from typing import Optional, Union

from django.conf import settings
from django.db import models

from .course import Course
from .resource import Resource
from .user import User


# Ignore: See explanation in UserManager.
class StarredManager(models.Manager):  # type: ignore[type-arg]
    def perform_star(
        self, user: User, target: Union[Course, Resource]
    ) -> Optional["Starred"]:
        """Automatically create a new star or delete one if it already exists."""

        if isinstance(target, Course):
            starred = self.check_existing_starred(user, course=target)
        elif isinstance(target, Resource):
            starred = self.check_existing_starred(user, resource=target)
        else:
            raise TypeError(f"Invalid target type for Starred: {type(target)}")

        return starred

    def check_existing_starred(
        self, user: User, **target: Union[Course, Resource]
    ) -> Optional["Starred"]:
        try:
            # Ignore: user.stars not yet defined.
            starred = user.stars.get(**target)  # type: ignore [attr-defined]
            starred.delete()
            return None

        except Starred.DoesNotExist:
            starred = self.model(**target)
            starred.user = user
            starred.save()
            return starred


class Starred(models.Model):
    """Models a user's starred course or resource."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stars"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=True, blank=True, related_name="stars"
    )
    resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, null=True, blank=True, related_name="stars"
    )

    objects = StarredManager()

    class Meta:
        unique_together = ("user", "course", "resource")

    def __str__(self) -> str:
        if self.course is not None:
            return f"{self.user} - {self.course}"
        elif self.resource is not None:
            return f"{self.user} - {self.resource}"
        else:
            raise ValueError("Invalid starred object.")
