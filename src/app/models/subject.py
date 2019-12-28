from django.db import models

from .school import School


class Subject(models.Model):
    """Models one studiable subject, e.g. Computer Engineering."""

    name = models.CharField(max_length=100)
    schools = models.ManyToManyField(School, related_name="subjects")

    def __str__(self) -> str:
        return f"{self.name}"
