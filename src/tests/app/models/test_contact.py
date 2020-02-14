import pytest
from pytest import fixture

from app.models import Contact, ContactType, User


def test_str(db: fixture) -> None:
    contact1 = Contact.objects.get(pk=1)
    assert str(contact1) == "Contact by testfeedback@test.com, type: Feedback"

    contact2 = Contact.objects.get(pk=2)
    assert str(contact2) == "Contact by no-email, type: Feedback"


def test_manager_create_ok(db: fixture) -> None:
    feedback_type = ContactType.objects.get(pk=1)
    contact3 = Contact.objects.create_contact(
        contact_type=feedback_type,
        message="Sending some feedback",
        user_or_email="some@email.com",
    )

    user = User.objects.get(pk=2)
    contact4 = Contact.objects.create_contact(
        contact_type=feedback_type, message="Sending some feedback", user_or_email=user
    )

    assert Contact.objects.get(pk=3) == contact3
    assert Contact.objects.get(pk=4) == contact4


def test_manager_create_bad_contact(db: fixture) -> None:
    feedback_type = ContactType.objects.get(pk=1)

    with pytest.raises(TypeError):
        Contact.objects.create_contact(
            contact_type=feedback_type, message="Sending some feedback", user_or_email=1
        )
