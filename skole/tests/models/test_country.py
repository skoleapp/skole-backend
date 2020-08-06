from skole.models import Country
from skole.utils.types import Fixture


def test_str(db: Fixture) -> None:
    country1 = Country.objects.get(pk=1)
    assert str(country1) == "Finland"
