import pytest

from skole.models import City


@pytest.mark.django_db
def test_str() -> None:
    city1 = City.objects.get(pk=1)
    assert str(city1) == "Turku"

    city2 = City.objects.get(pk=2)
    assert str(city2) == "Helsinki"
