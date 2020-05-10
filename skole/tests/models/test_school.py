from pytest import fixture

from skole.models import School


def test_str(db: fixture) -> None:
    school1 = School.objects.get(pk=1)
    assert str(school1) == "University of Turku"

    school2 = School.objects.get(pk=2)
    assert str(school2) == "Aalto University"


def test_subjects(db: fixture) -> None:
    school = School.objects.get(pk=1)
    assert school.subjects.get(pk=1).name == "Computer Engineering"
