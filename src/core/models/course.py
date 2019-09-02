from django.db import models

from .school import School
from.user import User


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, null=True, blank=True)
    subject = models.ForeignKey(School, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL)  # TODO: custom deletor, which marks the user as some anonymous user
    created_at = models.DateField(auto_now=True)
