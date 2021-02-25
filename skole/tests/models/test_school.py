import pytest

from skole.models import School


@pytest.mark.django_db
def test_str() -> None:
    school1 = School.objects.get(pk=1)
    assert str(school1) == "University of Turku"

    school2 = School.objects.get(pk=2)
    assert str(school2) == "Aalto University"


@pytest.mark.django_db
def test_subjects() -> None:
    school = School.objects.get(pk=1)
    assert school.subjects.get(pk=1).name == "Computer Engineering"
