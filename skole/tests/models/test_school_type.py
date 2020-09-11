from skole.models import SchoolType
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    school_type1 = SchoolType.objects.get(pk=1)
    assert str(school_type1) == "University"

    school_type2 = SchoolType.objects.get(pk=2)
    assert str(school_type2) == "University of Applied Sciences"
