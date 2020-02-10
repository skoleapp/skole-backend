from django.db import models

from .user import User


class BetaCode(models.Model):
    code = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
