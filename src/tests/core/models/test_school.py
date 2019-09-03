from core.models import School
from core.utils import UNIVERSITY, UNIVERSITY_OF_APPLIED_SCIENCES, HIGH_SCHOOL


def test_create_school(db):
    school = School.objects.create_school(
        school_type=UNIVERSITY,
        name="University of Turku",
        city="Turku",
        country="Finland",
    )
    assert str(school) == "University of Turku"

