from django.db import models
from django.db.models import QuerySet

from .school import School
from .subject import Subject
from .user import User


class CourseManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        return qs.annotate(resource_count=models.Count('resources'))


class Course(models.Model):
    """Models one course."""

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, null=True, blank=True)
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
        code = self.code if self.code is not None else ""
        name = self.name if self.name is not None else ""
        # One space in between if both `code` and `name` are non-empty strings,
        # otherwise no need to have a space in between.
        return f"{code}{' ' * bool(code and name)}{name}"
