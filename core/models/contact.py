from typing import Union

from django.db import models

from .contact_type import ContactType
from .user import User


class ContactManager(models.Manager):  # type: ignore[type-arg]
    def create_contact(
        self,
        contact_type: ContactType,
        message: str,
        username_or_email: Union[str, User],
    ) -> "Contact":
        contact = self.model(contact_type=contact_type, message=message)

        if isinstance(username_or_email, str):
            contact.email = username_or_email
        elif isinstance(username_or_email, User):
            contact.user = username_or_email
        else:
            raise TypeError("Contact needs an email or a User.")

        contact.save()
        return contact


class Contact(models.Model):
    """Models one contact send through the API, e.g. a filled feedback form."""

    contact_type = models.ForeignKey(
        ContactType, on_delete=models.PROTECT, related_name="contacts"
    )
    email = models.EmailField(unique=False, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="contacts", null=True
    )
    message = models.TextField(max_length=2000, blank=True)

    objects = ContactManager()

    def __str__(self) -> str:
        return f"Contact by {self.email or 'no-email'}, type: {self.contact_type}"
