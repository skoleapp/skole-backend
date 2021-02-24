from skole.models import MarketingEmailSender
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    marketing_email_sender = MarketingEmailSender.objects.get(pk=1)
    assert str(marketing_email_sender) == "Sender from Skole <sender@test.com>"
