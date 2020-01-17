from django.db import models

from .city import City


class SchoolType(models.Model):
    """Models one type of school, e.g. University of High School."""

    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name}"


class School(models.Model):
    """Models one school on the platform."""

    school_type = models.ForeignKey(
        SchoolType, on_delete=models.PROTECT, related_name="schools"
    )
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="schools")

    def __str__(self) -> str:
        return f"{self.name}"
