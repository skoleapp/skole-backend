from django.db import models
from parler.models import TranslatedFields

from skole.models.base import TranslatableSkoleModel


class ActivityType(TranslatableSkoleModel):
    """Models one type of activity, e.g. comment reply."""

    # E.g comment_reply, course_comment, resource_comment
    name = models.CharField(max_length=100, unique=True)
    translations = TranslatedFields(description=models.CharField(max_length=2000))

    def __str__(self) -> str:
        return f"{self.name}"
