from typing import TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet

from .city import City
from .school_type import SchoolType
from .subject import Subject

if TYPE_CHECKING:
    from .course import Course


class School(models.Model):
    """Models one school on the platform."""

    school_type = models.ForeignKey(
        SchoolType, on_delete=models.PROTECT, related_name="schools"
    )
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="schools")

    if TYPE_CHECKING:
        courses: "QuerySet[Course]"

    def __str__(self) -> str:
        return f"{self.name}"

    @property
    def subjects(self) -> "QuerySet[Subject]":
        return Subject.objects.filter(courses__in=self.courses.all())

    @property
    def subject_count(self) -> int:
        return self.courses.prefetch_related("subject").count()

    @property
    def course_count(self) -> int:
        return self.courses.count()
