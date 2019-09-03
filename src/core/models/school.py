import datetime

from django.db import models
from ..utils import SCHOOL_TYPES


class SchoolManager(models.Manager):
    def create_school(self, school_type: str, name: str,
                      city: str, country: str) -> 'School':
        school = self.model(
            school_type=school_type,
            name=name,
            city=city,
            country=country,
        )
        school.save()
        return school


class School(models.Model):
    """Abstract base class for all schools."""
    school_type = models.CharField(choices=SCHOOL_TYPES, max_length=30)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = SchoolManager()

    def __str__(self) -> str:
        return f"{self.name}"

