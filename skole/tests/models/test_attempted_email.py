import pytest

from skole.models import AttemptedEmail


@pytest.mark.django_db
def test_str() -> None:
    attempt = AttemptedEmail.objects.create(email="email@test.test")
    assert str(attempt) == "email@test.test, attempts: 0, not whitelisted"

    attempt.attempts = 15
    attempt.is_whitelisted = True
    attempt.save()
    assert str(attempt) == "email@test.test, attempts: 15, whitelisted"
