from django.db import models
from parler.models import TranslatedFields

from .base import TranslatableSkoleModel
from .country import Country


class City(TranslatableSkoleModel):
    """Models one city, e.g. Turku or Helsinki."""

    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, related_name="cities"
    )

    translations = TranslatedFields(name=models.CharField(max_length=100))

    def __str__(self) -> str:
        return f"{self.name}"
