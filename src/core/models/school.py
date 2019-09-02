from django.db import models


class School(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    created_at = models.DateField(auto_now=True)

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
