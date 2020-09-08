from django.db import models
from parler.models import TranslatedFields

from .base import TranslatableSkoleModel


class Subject(TranslatableSkoleModel):
    """Models one studyable subject, e.g. Computer Engineering."""

    translations = TranslatedFields(name=models.CharField(max_length=100))

    def __str__(self) -> str:
        return f"{self.name}"
