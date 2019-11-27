from django.db import models


class SchoolType(models.Model):
    """Models one type of school, e.g. University of High School."""

    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name}"
