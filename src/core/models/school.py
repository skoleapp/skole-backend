from django.db import models
from ..utils import SCHOOL_TYPES


class School(models.Model):
    """Abstract base class for all schools."""
    school_type = models.CharField(choices=SCHOOL_TYPES, max_length=30)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name}"

