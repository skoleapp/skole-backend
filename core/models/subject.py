from django.db import models


class Subject(models.Model):
    """Models one studiable subject, e.g. Computer Engineering."""

    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name}"
