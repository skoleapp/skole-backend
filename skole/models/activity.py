from django.conf import settings
from django.db import models

from .activity_type import ActivityType


class Activity(models.Model):
    """Models a single activity of a users activity feed."""

    # A user who's activity feed this activity belongs to.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activities"
    )

    # A user who creates the activity, e.g. user replying to a comment.
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="target_activities",
        null=True,
    )

    activity_type = models.ForeignKey(
        ActivityType, on_delete=models.PROTECT, related_name="activities"
    )

    def __str__(self) -> str:
        return self.activity_type
