from django.conf import settings
from django.db import models
from django.db.models import QuerySet

from .base import SkoleManager, SkoleModel
from .user import User


class ActivityManager(SkoleManager):
    def mark_all_as_read(self, user: User) -> "QuerySet[Activity]":
        """Mark all activities as read for a user."""
        qs = self.filter(user=user)
        qs.update(read=True)
        return qs


class Activity(SkoleModel):
    """Models a single activity of a users activity feed."""

    # A user who's activity feed this activity belongs to.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity"
    )

    # A user who causes the activity, e.g. a user replying to a comment.
    # Can also be null when a non-logged in user is the commenter.
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name="target_activities",
    )

    activity_type = models.ForeignKey(
        "skole.ActivityType", on_delete=models.PROTECT, related_name="activities"
    )

    # The different objects that can have activity appear in them.
    course = models.ForeignKey(
        "skole.Course", on_delete=models.CASCADE, null=True, blank=True,
    )
    resource = models.ForeignKey(
        "skole.Resource", on_delete=models.CASCADE, null=True, blank=True,
    )
    comment = models.ForeignKey(
        "skole.Comment", on_delete=models.CASCADE, null=True, blank=True,
    )

    read = models.BooleanField(default=False)

    # Ignore: Mypy somehow thinks that this is incompatible with the super class.
    objects = ActivityManager()  # type: ignore[assignment]

    def __str__(self) -> str:
        return f"{self.activity_type.name}"
