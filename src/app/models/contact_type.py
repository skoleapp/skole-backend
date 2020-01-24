from django.db import models


class ContactType(models.Model):
    """Models one type of contact request,
    e.g. request for a new school or a business enquiry.
    """

    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name}"
