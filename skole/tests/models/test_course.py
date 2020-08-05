from skole.models import Course
from skole.utils.types import Fixture


def test_str(db: Fixture) -> None:
    course1 = Course.objects.get(pk=1)
    assert str(course1) == "Test Engineering Course 1 TEST0001"

    course3 = Course.objects.get(pk=2)
    course3.code = ""
    assert str(course3) == "Test Engineering Course 2"
