from django.db import models
from django.db.models import QuerySet
from parler.models import TranslatedFields

from .base import TranslatableSkoleModel
from .city import City
from .school_type import SchoolType
from .subject import Subject


class School(TranslatableSkoleModel):
    """Models one school on the platform."""

    school_type = models.ForeignKey(
        SchoolType, on_delete=models.PROTECT, related_name="schools"
    )

    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="schools")
    translations = TranslatedFields(name=models.CharField(max_length=100))

    def __str__(self) -> str:
        return f"{self.name}"

    @property
    def subjects(self) -> "QuerySet[Subject]":
        return Subject.objects.filter(courses__in=self.courses.all()).distinct()
