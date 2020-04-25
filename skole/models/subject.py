from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class Subject(TranslatableModel):
    """Models one studiable subject, e.g. Computer Engineering."""

    translations = TranslatedFields(name=models.CharField(max_length=100))

    def __str__(self) -> str:
        return f"{self.name}"
