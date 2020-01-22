from django.db import models


class ResourceType(models.Model):
    """Models one type of resource, e.g. an exam or a note."""

    name = models.CharField(max_length=100, unique=True)
    has_parts = models.BooleanField()

    def __str__(self) -> str:
        return f"{self.name}"
