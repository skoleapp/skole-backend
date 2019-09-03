import datetime

from django.db import models

from .faculty import Faculty


class Facility(models.Model):
    """Models one university facility (=laitos).
    For example "Department of Future Technologies".
    """
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name}"
