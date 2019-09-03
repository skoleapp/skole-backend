from django.db import models

from .faculty import Faculty
from .school import School


class Subject(models.Model):
    """Models one studiable subject.
    For example "computer engineering".
    """
    faculty = models.ManyToManyField(Faculty)
    name = models.CharField(max_length=100)
    school = models.ManyToManyField(School)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name}, {self.school.name}"
