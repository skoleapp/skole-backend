from django.conf import settings
from django.db import models
from parler.models import TranslatableModel, TranslatedFields

from .comment import Comment
from .course import Course
from .resource import Resource


class Activity(TranslatableModel):
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

    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True,)

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True,)

    # Currently all activities are related to comments so technically this would not have to be nullable.
    # However, if we decide to add other types of activities than comment notifications, this field would have to be nullable.
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True,)

    translations = TranslatedFields(description=models.CharField(max_length=2000),)

    def __str__(self) -> str:
        if self.target_user:
            return f"{self.target_user.username} {self.description}"

        return f"{self.description}"
