from django.db import models
from django.db.models import QuerySet
from parler.models import TranslatedFields

from .base import TranslatableSkoleModel
from .subject import Subject


class School(TranslatableSkoleModel):
    """Models one school on the platform."""

    school_type = models.ForeignKey(
        "skole.SchoolType", on_delete=models.PROTECT, related_name="schools"
    )

    city = models.ForeignKey(
        "skole.City", on_delete=models.PROTECT, related_name="schools"
    )
    translations = TranslatedFields(name=models.CharField(max_length=100))

    def __str__(self) -> str:
        return f"{self.name}"

    @property
    def subjects(self) -> QuerySet[Subject]:
        return Subject.objects.filter(courses__in=self.courses.all()).distinct()
