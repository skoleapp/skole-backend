from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class SchoolType(TranslatableModel):
    """Models one type of school, e.g. University of High School."""

    translations = TranslatedFields(name=models.CharField(max_length=100))

    def __str__(self) -> str:
        return f"{self.name}"
