from autoslug import AutoSlugField
from django.db import models
from parler.models import TranslatedFields

from skole.models.base import TranslatableSkoleModel


class Country(TranslatableSkoleModel):
    """Models one country, e.g. Finland or Sweden."""

    slug = AutoSlugField(
        null=True,
        default=None,
        populate_from="__str__",
        unique=True,
    )

    translations = TranslatedFields(name=models.CharField(max_length=100))

    def __str__(self) -> str:
        return f"{self.name}"
