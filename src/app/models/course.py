from django.db import models

from app.models.school import School
from app.models.subject import Subject
from app.models.user import User


class Course(models.Model):
    """Models one course."""

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="courses")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="courses")
    # TODO: custom deletor, which marks the user as some anonymous user
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_courses")

    points = models.IntegerField(default=0)

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        code = self.code if self.code is not None else ""
        name = self.name if self.name is not None else ""
        # One space in between if both `code` and `name` are non-empty strings,
        # otherwise no need to have a space in between.
        return f"{code}{' ' * bool(code and name)}{name}"
