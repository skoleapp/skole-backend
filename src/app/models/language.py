from django.db import models


class Language(models.Model):
    """Models one language, e.g. Finnish or English."""

    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name}"
