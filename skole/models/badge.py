from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models
from parler.models import TranslatedFields

from skole.models.base import TranslatableSkoleModel
from skole.utils.constants import BADGE_TIER_CHOICES


class Badge(TranslatableSkoleModel):
    """Models a badge awarded for a user, e.g `Moderator`."""

    _identifier_field = "identifier"

    identifier = models.CharField(
        max_length=100,
        default="",  # To make this compatible with existing data.
    )
    steps = models.IntegerField(null=True, validators=[MinValueValidator(1)])
    completion_score = models.IntegerField(default=0)
    tier = models.CharField(choices=BADGE_TIER_CHOICES, max_length=20, default="bronze")

    translations = TranslatedFields(
        name=models.CharField(max_length=100),
        description=models.TextField(max_length=2000, blank=True),
    )

    # Whether `award_badges` management command has made sure that this badge has been
    # retroactively awarded to all users that should get it. Setting this makes it so
    # that we don't end up doing unnecessary work in the management command every time
    # during app startup.
    made_available = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.name}"
