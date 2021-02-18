from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import QuerySet

from .base import SkoleManager, SkoleModel
from .user import User


class ActivityManager(SkoleManager["Activity"]):
    def mark_all_as_read(self, user: User) -> QuerySet[Activity]:
        """Mark all activities as read for a user."""
        qs = self.filter(user=user)
        qs.update(read=True)
        return qs


class Activity(SkoleModel):
    """Models a single activity of a users activity feed."""

    _identifier_field = "activity_type"

    # A user who's activity feed this activity belongs to.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activities"
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
        "skole.Course", on_delete=models.CASCADE, null=True, blank=True
    )

    resource = models.ForeignKey(
        "skole.Resource", on_delete=models.CASCADE, null=True, blank=True
    )

    comment = models.ForeignKey(
        "skole.Comment", on_delete=models.CASCADE, null=True, blank=True
    )

    read = models.BooleanField(default=False)

    objects = ActivityManager()

    def __str__(self) -> str:
        return f"{self.activity_type.name}"
