from skole.models import Subject
from skole.utils.types import Fixture


def test_str(db: Fixture) -> None:
    subject1 = Subject.objects.get(pk=1)
    assert str(subject1) == "Computer Engineering"

    subject2 = Subject.objects.get(pk=2)
    assert str(subject2) == "Computer Science"
