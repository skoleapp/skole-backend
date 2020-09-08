from skole.models import Resource
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    resource1 = Resource.objects.get(pk=1)
    assert str(resource1) == "Sample exam 1"

    resource2 = Resource.objects.get(pk=2)
    assert str(resource2) == "Sample exam 2"
