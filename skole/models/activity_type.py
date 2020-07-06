from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class ActivityType(TranslatableModel):
    """Models one type of activity, e.g. comment reply."""

    translations = TranslatedFields(
        name=models.CharField(max_length=100),
        description=models.CharField(max_length=200),
    )

    def __str__(self) -> str:
        return f"{self.name}"
