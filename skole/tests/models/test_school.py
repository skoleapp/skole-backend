from skole.models import School
from skole.utils.types import Fixture


def test_str(db: Fixture) -> None:
    school1 = School.objects.get(pk=1)
    assert str(school1) == "University of Turku"

    school2 = School.objects.get(pk=2)
    assert str(school2) == "Aalto University"


def test_subjects(db: Fixture) -> None:
    school = School.objects.get(pk=1)
    assert school.subjects.get(pk=1).name == "Computer Engineering"
