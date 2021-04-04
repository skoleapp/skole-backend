import pytest
from django.contrib.auth import get_user_model

from skole.models import ReferralCode


@pytest.mark.django_db
def test_str() -> None:
    referral_code = ReferralCode.objects.get(pk=1)
    assert (
        str(referral_code) == f"{referral_code.code} - Usages: {referral_code.usages}"
    )


@pytest.mark.django_db
def test_use_code() -> None:
    referral_code = ReferralCode.objects.get(pk=1)
    assert referral_code.usages == 2
    user = get_user_model().objects.get(pk=12)
    referral_code.use_code(user=user)
    assert referral_code.usages == 1
