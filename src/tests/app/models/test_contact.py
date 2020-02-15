import pytest
from django.contrib.auth import get_user_model
from pytest import fixture

from app.models import Contact, ContactType


def test_str(db: fixture) -> None:
    contact1 = Contact.objects.get(pk=1)
    assert str(contact1) == "Contact by testfeedback@test.com, type: Feedback"

    contact2 = Contact.objects.get(pk=2)
    assert str(contact2) == "Contact by no-email, type: Feedback"


def test_manager_create_ok(db: fixture) -> None:
    contact_type = ContactType.objects.get(pk=1)
    message = "Sending some feedback"
    email = "some@email.com"
    contact3 = Contact.objects.create_contact(
        contact_type=contact_type, message=message, user_or_email=email,
    )
    assert contact3.contact_type == contact_type
    assert contact3.message == message
    assert contact3.user is None
    assert contact3.email == email

    user = get_user_model().objects.get(pk=2)
    contact4 = Contact.objects.create_contact(
        contact_type=contact_type, message=message, user_or_email=user,
    )
    assert contact4.contact_type == contact_type
    assert contact4.message == message
    assert contact4.user == user
    assert contact4.email == ""


def test_manager_create_bad_contact(db: fixture) -> None:
    feedback_type = ContactType.objects.get(pk=1)

    with pytest.raises(TypeError):
        Contact.objects.create_contact(
            contact_type=feedback_type, message="Sending some feedback", user_or_email=1  # type: ignore[arg-type]
        )
