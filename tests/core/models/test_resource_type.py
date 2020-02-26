from pytest import fixture

from core.models import ResourceType


def test_str(db: fixture) -> None:
    resource_type1 = ResourceType.objects.get(pk=1)
    assert str(resource_type1) == "Exam"

    resource_type2 = ResourceType.objects.get(pk=2)
    assert str(resource_type2) == "Exercise"
