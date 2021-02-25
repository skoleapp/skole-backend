import pytest

from skole.models import Country


@pytest.mark.django_db
def test_str() -> None:
    country1 = Country.objects.get(pk=1)
    assert str(country1) == "Finland"
