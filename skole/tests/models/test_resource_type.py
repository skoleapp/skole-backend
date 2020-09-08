from skole.models import ResourceType
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    resource_type1 = ResourceType.objects.get(pk=1)
    assert str(resource_type1) == "Exam"

    resource_type2 = ResourceType.objects.get(pk=2)
    assert str(resource_type2) == "Exercise"
