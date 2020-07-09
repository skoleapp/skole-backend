from django.conf import settings
from django.db import models
from django.db.models import QuerySet

from .activity_type import ActivityType
from .comment import Comment
from .course import Course
from .resource import Resource
from .user import User


# Ignore: See explanation in UserManager.
class ActivityManager(models.Manager):  # type: ignore[type-arg]
    @staticmethod
    def mark_read(activity: "Activity", read: bool) -> "Activity":
        activity.read = read
        activity.save()
        return activity

    def mark_all_as_read(self, user: User) -> "QuerySet[Activity]":
        qs = self.filter(user=user)

        for item in qs:
            item.read = True
            item.save()

        return qs


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

    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True,)
    resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, null=True, blank=True,
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, blank=True,
    )
    read = models.BooleanField(default=False)
    objects = ActivityManager()

    def __str__(self) -> str:
        return f"{self.activity_type.name}"
