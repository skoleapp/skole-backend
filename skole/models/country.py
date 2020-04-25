from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class Country(TranslatableModel):
    """Models one country, e.g. Finland or Sweden."""

    translations = TranslatedFields(name=models.CharField(max_length=100))

    def __str__(self) -> str:
        return f"{self.name}"
