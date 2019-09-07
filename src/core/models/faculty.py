from django.db import models

from .school import School


class Faculty(models.Model):
    """Models one university faculty (=tiedekunta).
    For example "Faculty of Science and Engineering".
    """
    name = models.CharField(max_length=100)
    university = models.ForeignKey(School, on_delete=models.CASCADE)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name}"

