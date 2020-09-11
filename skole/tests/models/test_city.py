from skole.models import City
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    city1 = City.objects.get(pk=1)
    assert str(city1) == "Turku"

    city2 = City.objects.get(pk=2)
    assert str(city2) == "Helsinki"
