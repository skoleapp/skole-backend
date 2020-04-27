from pytest import fixture

from skole.models import City


def test_str(db: fixture) -> None:
    city1 = City.objects.get(pk=1)
    assert str(city1) == "Turku"

    city2 = City.objects.get(pk=2)
    assert str(city2) == "Helsinki"
