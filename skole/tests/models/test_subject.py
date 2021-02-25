import pytest

from skole.models import Subject


@pytest.mark.django_db
def test_str() -> None:
    subject1 = Subject.objects.get(pk=1)
    assert str(subject1) == "Computer Engineering"

    subject2 = Subject.objects.get(pk=2)
    assert str(subject2) == "Computer Science"
