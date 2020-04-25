from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class ResourceType(TranslatableModel):
    """Models one type of resource, e.g. an exam or a note."""

    translations = TranslatedFields(name=models.CharField(max_length=100))

    def __str__(self) -> str:
        return f"{self.name}"
