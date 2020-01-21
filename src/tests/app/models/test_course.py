from pytest import fixture

from app.models import Course


def test_str(db: fixture) -> None:
    course1 = Course.objects.get(pk=1)
    assert str(course1) == "TEST0001 Test Engineering Course 1"

    course2 = Course.objects.get(pk=2)
    course2.name = None
    assert str(course2) == "TEST0002"

    course3 = Course.objects.get(pk=3)
    course3.code = None
    assert str(course3) == "Test Engineering Course 3"
