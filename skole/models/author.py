from django.conf import settings
from django.db import models

from skole.models.base import SkoleModel


class Author(SkoleModel):
    """Models the author (=copyright owner) of a resource."""

    _identifier_field = "name"

    # Only one of these two will be set at a time.
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.name}"
