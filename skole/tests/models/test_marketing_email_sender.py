import pytest

from skole.models import MarketingEmailSender


@pytest.mark.django_db
def test_str() -> None:
    marketing_email_sender = MarketingEmailSender.objects.get(pk=1)
    assert str(marketing_email_sender) == "Sender from Skole <sender@test.com>"
