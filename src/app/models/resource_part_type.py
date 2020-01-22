from django.db import models


class ResourcePartType(models.Model):
    """Models one type of resource resource part, e.g. an exercise or part of a note."""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return f"{self.name}"
