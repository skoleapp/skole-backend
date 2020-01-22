from pytest import fixture

from app.models import Country


def test_str(db: fixture) -> None:
    country1 = Country.objects.get(pk=1)
    assert str(country1) == "Finland"
