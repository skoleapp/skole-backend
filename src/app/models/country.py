from django.db import models


class Country(models.Model):
    """Models one country, e.g. Finland or Sweden."""

    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name}"
