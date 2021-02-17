from skole.models import MarketingEmail
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    marketing_email = MarketingEmail.objects.get(pk=1)
    assert str(marketing_email) == "Test Product Update Email"
