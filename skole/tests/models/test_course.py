from skole.models import Course
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    course1 = Course.objects.get(pk=1)
    assert str(course1) == "Test Engineering Course 1 (TEST0001)"

    course2 = Course.objects.get(pk=2)
    course2.codes = ""
    assert str(course2) == "Test Engineering Course 2"

    course3 = Course.objects.get(pk=3)
    assert str(course3) == "Test Engineering Course 3 (TEST0003, TEST0033, TEST0333)"
