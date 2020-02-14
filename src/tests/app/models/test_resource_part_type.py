from pytest import fixture

from app.models import ResourcePartType


def test_str(db: fixture) -> None:
    resource_part_type1 = ResourcePartType.objects.get(pk=1)
    assert str(resource_part_type1) == "Exercise"

    resource_part_type2 = ResourcePartType.objects.get(pk=2)
    assert str(resource_part_type2) == "Note Part"
