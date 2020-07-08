from django.conf import settings
from django.db import models

from .activity_type import ActivityType
from .comment import Comment
from .course import Course
from .resource import Resource


class Activity(models.Model):
    """Models a single activity of a users activity feed."""

    # A user who's activity feed this activity belongs to.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity"
    )

    # A user who creates the activity, e.g. user replying to a comment.
    # This field is nullable in case we want to make activities that do not involve a target user and are only defined by the description.
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name="target_activities",
    )

    activity_type = models.ForeignKey(
        ActivityType, on_delete=models.PROTECT, related_name="activities"
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True,)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True,)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True,)

    def __str__(self) -> str:
        return f"{self.activity_type}"
