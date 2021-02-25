import pytest

from skole.models import MarketingEmail


@pytest.mark.django_db
def test_str() -> None:
    marketing_email = MarketingEmail.objects.get(pk=1)
    assert str(marketing_email) == "Test Product Update Email"
