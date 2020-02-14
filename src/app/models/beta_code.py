from django.db import models

from .user import User


class BetaCode(models.Model):
    code = models.CharField(max_length=6, unique=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
