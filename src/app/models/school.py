from django.db import models

from app.models.city import City
from app.models.school_type import SchoolType


class School(models.Model):
    """Models one school on the platform."""

    school_type = models.ForeignKey(SchoolType, on_delete=models.PROTECT, related_name="schools")
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="schools")

    def __str__(self) -> str:
        return f"{self.name}"
