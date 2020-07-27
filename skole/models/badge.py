from django.conf import settings
from django.db import models
from parler.models import TranslatableModel, TranslatedFields

from .base import SkoleModel


class Badge(SkoleModel, TranslatableModel):
    """Models a badge awarded for a user, e.g `Moderator`."""

    user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="badges")

    translations = TranslatedFields(
        name=models.CharField(max_length=100),
        description=models.TextField(max_length=2000, blank=True),
    )

    def __str__(self) -> str:
        return f"{self.name}"
