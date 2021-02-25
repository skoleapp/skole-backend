import pytest

from skole.models import ResourceType


@pytest.mark.django_db
def test_str() -> None:
    resource_type1 = ResourceType.objects.get(pk=1)
    assert str(resource_type1) == "Exercise"

    resource_type2 = ResourceType.objects.get(pk=2)
    assert str(resource_type2) == "Note"
