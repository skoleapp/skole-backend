from rest_framework.authtoken.models import Token

from core.models import User
from core.utils import ENGLISH, FINNISH


def test_str(user):
    assert str(user) == "testuser"


def test_create_superuser(db):
    user = User.objects.create_superuser(username="root", password="root")
    assert user.is_superuser
    assert user.is_staff
    assert str(user) == "root"


def test_set_password(db, user):
    new_pass = "new pass"
    user = User.objects.set_password(user, new_pass)
    assert user.check_password(new_pass)


def test_set_language(db, user):
    assert user.language == ENGLISH
    User.objects.set_language(user, FINNISH)
    assert user.language == FINNISH


def test_refresh_token(db, user):
    token = Token.objects.create(user=user)
    refresh_token = User.objects.refresh_token(user=user, token=token)
    assert token != refresh_token
