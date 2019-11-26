from django.db import models


class ResourceType(models.Model):
    """Models one type of resource, e.g. an Exam or a Note."""

    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name}"
