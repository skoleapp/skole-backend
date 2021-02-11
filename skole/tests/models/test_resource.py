from skole.models import Resource
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    resource1 = Resource.objects.get(pk=1)
    assert str(resource1) == "Sample Exam 1 2012-12-12"

    resource2 = Resource.objects.get(pk=2)
    assert str(resource2) == "Sample Exam 2 2012-12-12"


def test_increment_downloads(db: Fixture) -> None:
    resource = Resource.objects.get(pk=1)
    assert resource.downloads == 0
    resource = Resource.objects.increment_downloads(resource)
    assert resource.downloads == 1
