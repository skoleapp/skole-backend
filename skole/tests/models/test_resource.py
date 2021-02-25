import pytest

from skole.models import Resource


@pytest.mark.django_db
def test_str() -> None:
    resource1 = Resource.objects.get(pk=1)
    assert str(resource1) == "Sample Exam 1 2012-12-12"

    resource2 = Resource.objects.get(pk=2)
    assert str(resource2) == "Sample Exam 2 2012-12-12"


@pytest.mark.django_db
def test_increment_downloads() -> None:
    resource = Resource.objects.get(pk=1)
    assert resource.downloads == 0
    resource = Resource.objects.increment_downloads(resource)
    assert resource.downloads == 1
