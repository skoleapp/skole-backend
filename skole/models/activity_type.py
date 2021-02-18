from django.db import models
from parler.models import TranslatedFields

from .base import TranslatableSkoleModel


class ActivityType(TranslatableSkoleModel):
    """Models one type of activity, e.g. comment reply."""

    _identifier_field = "name"

    # E.g comment_reply, course_comment, resource_comment
    name = models.CharField(max_length=100, unique=True)
    translations = TranslatedFields(description=models.CharField(max_length=2000))

    def __str__(self) -> str:
        return f"{self.name}"
