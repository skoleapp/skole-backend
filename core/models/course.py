from django.db import models
from django.db.models import QuerySet

from .school import School
from .subject import Subject
from .user import User


class CourseManager(models.Manager):  # type: ignore[type-arg]
    def get_queryset(self) -> "QuerySet[Course]":
        qs = super().get_queryset()
        return qs.annotate(resource_count=models.Count("resources"))


class Course(models.Model):
    """Models one course."""

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, blank=True)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="courses", null=True, blank=True
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="courses")
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_courses",
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = CourseManager()

    def __str__(self) -> str:
        if self.code:
            return f"{self.code} {self.name}"
        else:
            return f"{self.name}"
