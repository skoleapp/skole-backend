from django.db import models

from .faculty import Faculty


class Facility(models.Model):
    """Models one university facility (=laitos).
    For example "Department of Future Technologies".
    """
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now=True)
