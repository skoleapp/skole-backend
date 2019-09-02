from django.db import models

from .school import University


class Faculty(models.Model):
    """Models one university faculty (=tiedekunta).
    For example "Faculty of Science and Engineering".
    """
    name = models.CharField(max_length=100)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now=True)
