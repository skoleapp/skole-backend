from autoslug import AutoSlugField
from django.db import models
from parler.models import TranslatedFields

from .base import TranslatableSkoleModel


class City(TranslatableSkoleModel):
    """Models one city, e.g. Turku or Helsinki."""

    slug = AutoSlugField(
        null=True,
        default=None,
        populate_from="__str__",
        unique=True,
    )

    country = models.ForeignKey(
        "skole.Country", on_delete=models.PROTECT, related_name="cities"
    )

    translations = TranslatedFields(name=models.CharField(max_length=100))

    def __str__(self) -> str:
        return f"{self.name}"
