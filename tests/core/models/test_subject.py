from pytest import fixture

from core.models import Subject


def test_str(db: fixture) -> None:
    subject1 = Subject.objects.get(pk=1)
    assert str(subject1) == "Computer Engineering"

    subject2 = Subject.objects.get(pk=2)
    assert str(subject2) == "Computer Science"
