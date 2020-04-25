from django.db import models
from django.db.models import QuerySet
from parler.models import TranslatableModel, TranslatedFields

from .city import City
from .school_type import SchoolType
from .subject import Subject


class School(TranslatableModel):
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
        return Subject.objects.filter(courses__in=self.courses.all()).distinct()  # type: ignore[attr-defined]

    @property
    def subject_count(self) -> int:
        return self.courses.values("subject").distinct().count()

    @property
    def course_count(self) -> int:
        return self.courses.count()  # type: ignore[attr-defined]
