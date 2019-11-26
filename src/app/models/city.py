from django.db import models

from .country import Country


class City(models.Model):
    """Models one city, e.g. Turku or Helsinki"""

    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="cities")

    def __str__(self) -> str:
        return f"{self.name}"
