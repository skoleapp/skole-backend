from django.db import models

from .school import University


class Faculty(models.Model):
    """Models one university faculty (=tiedekunta).
    For example "Faculty of Science and Engineering".
    """
    name = models.CharField(max_length=100)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

