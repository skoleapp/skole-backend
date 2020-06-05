from django.conf import settings
from django.db import models
from django.db.models import QuerySet, Sum, Value
from django.db.models.functions import Coalesce

from .school import School
from .subject import Subject


# Ignore: See explanation in UserManager.
class CourseManager(models.Manager):  # type: ignore[type-arg]
    def get_queryset(self) -> "QuerySet[Course]":
        qs = super().get_queryset()
        return qs.annotate(score=Coalesce(Sum("votes__status"), Value(0)))


class Course(models.Model):
    """Models one course."""

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, blank=True)

    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="courses", null=True, blank=True
    )

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="courses")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_courses",
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = CourseManager()

    # This value gets annotated in the manager's get_queryset.
    score: int

    def __str__(self) -> str:
        return f"{self.name} {self.code}" if self.code else self.name

    @property
    def resource_count(self) -> int:
        return self.resources.count()
