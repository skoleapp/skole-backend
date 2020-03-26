from typing import Optional, Union

from django.db import models

from core.models.course import Course
from core.models.resource import Resource
from core.models.user import User


# Ignore: See explanation in UserManager.
class StarManager(models.Manager):  # type: ignore[type-arg]
    def perform_star(
        self, user: User, target: Union[Course, Resource]
    ) -> Optional["Star"]:
        """Automatically create a new star or delete one if it already exists."""

        if isinstance(target, Course):
            star = self.check_existing_star(user, course=target)
        elif isinstance(target, Resource):
            star = self.check_existing_star(user, resource=target)
        else:
            raise TypeError(f"Invalid target type for Vote: {type(target)}")

        return star

    def check_existing_star(
        self, user: User, **target: Union[Course, Resource]
    ) -> Optional["Star"]:
        try:
            star = user.stars.get(**target)

            if star is not None:
                star.delete()
                return None

        except Star.DoesNotExist:
            star = self.model(**target)
            star.user = user
            star.save()
            return star


class Star(models.Model):
    """Models a user's star on either course or resource."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stars")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=True, blank=True, related_name="votes"
    )
    resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, null=True, blank=True, related_name="votes"
    )

    objects = StarManager()

    class Meta:
        unique_together = ("user", "course", "user")

    def __str__(self) -> str:
        return self.user.username
