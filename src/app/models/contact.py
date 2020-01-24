from typing import Union

from django.db import models

from .contact_type import ContactType
from .user import User


class ContactManager(models.Manager):
    def create_contact(
        self, contact_type: ContactType, message: str, user_or_email: Union[str, User]
    ) -> "Contact":
        contact = self.model(contact_type=contact_type, message=message)

        if isinstance(user_or_email, str):
            contact.email = user_or_email
        elif isinstance(user_or_email, User):
            contact.user = user_or_email
        else:
            raise TypeError("Contact needs an email or a User.")

        contact.save()
        return contact


class Contact(models.Model):
    """Models one contact send through the API, e.g. a filled feedback form."""

    contact_type = models.ForeignKey(
        ContactType, on_delete=models.PROTECT, related_name="contacts"
    )
    email = models.EmailField(unique=True, null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="contacts", null=True
    )
    message = models.TextField(max_length=2000, null=True, blank=True)

    objects = ContactManager()

    def __str__(self) -> str:
        return f"Contact by {self.email}, type: {self.contact_type}"
