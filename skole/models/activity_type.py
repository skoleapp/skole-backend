from __future__ import annotations

from django.db import models
from parler.models import TranslatedFields

from skole.models.base import TranslatableSkoleModel


class ActivityType(TranslatableSkoleModel):
    """Models one type of activity, e.g. comment reply."""

    _identifier_field = "identifier"

    # E.g comment_reply or thread_comment.
    identifier = models.CharField(max_length=100, unique=True)
    translations = TranslatedFields(description=models.CharField(max_length=2000))

    def __str__(self) -> str:
        return f"{self.identifier}"
