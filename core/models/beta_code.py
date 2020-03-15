from django.db import models


class BetaCode(models.Model):
    code = models.CharField(max_length=8, unique=True)
    usages = models.IntegerField()
