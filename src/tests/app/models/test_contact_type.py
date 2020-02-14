from pytest import fixture

from app.models import ContactType


def test_str(db: fixture) -> None:
    contact1 = ContactType.objects.get(pk=1)
    assert str(contact1) == "Feedback"

    contact2 = ContactType.objects.get(pk=2)
    assert str(contact2) == "Request School"
