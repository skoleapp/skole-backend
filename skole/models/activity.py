from django.conf import settings
from django.db import models
from parler.models import TranslatableModel, TranslatedFields


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
        related_name="target_activities",
        null=True,
    )

    translations = TranslatedFields(
        description=models.CharField(max_length=2000),
    )

    def __str__(self) -> str:
        if self.target_user:
            return f"{self.target_user.username} {self.description}"

        return f"{self.description}"
