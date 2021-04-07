import pytest
from django.contrib.auth import get_user_model

from skole.models import InviteCode


@pytest.mark.django_db
def test_str() -> None:
    invite_code = InviteCode.objects.get(pk=1)
    assert str(invite_code) == f"{invite_code.code} - Usages: {invite_code.usages}"


@pytest.mark.django_db
def test_use_code() -> None:
    invite_code = InviteCode.objects.get(pk=1)
    assert invite_code.usages == 2
    user = get_user_model().objects.get(pk=12)
    invite_code.use_code(user=user)
    assert invite_code.usages == 1
