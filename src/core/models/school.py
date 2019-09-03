from django.db import models


class School(models.Model):
    """Abstract base class for all schools."""
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class University(School):
    """Models one University."""
    pass


class AMK(School):
    """Models one Finnish ammattikorkeakoulu."""
    pass


class Lukio(School):
    """Models one Finnish Lukio."""
    pass
