from django.db import models
from django.db.models import Count, QuerySet, Sum
from django.db.models.functions import Coalesce

from .school import School
from .subject import Subject
from .user import User


# Ignore: See explanation in UserManager.
class CourseManager(models.Manager):  # type: ignore[type-arg]
    def get_queryset(self) -> "QuerySet[Course]":
        return super().get_queryset().annotate(resource_count=Count("resources"))


class Course(models.Model):
    """Models one course."""

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, blank=True)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="courses", null=True, blank=True
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="courses")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_courses",
    )

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = CourseManager()

    def __str__(self) -> str:
        return f"{self.name} {self.code}" if self.code else self.name

    @property
    def points(self) -> int:
        return self.votes.aggregate(points=Coalesce(Sum("status"), 0))["points"]
