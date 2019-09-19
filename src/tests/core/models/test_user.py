import datetime

from freezegun import freeze_time
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
    orig_key = token.key
    refresh_token = User.objects.refresh_token(user=user, token=token)
    assert orig_key == refresh_token.key
    assert token.key is not None

    current = datetime.datetime.utcnow() + datetime.timedelta(hours=23)
    time_string = datetime.datetime.strftime(current, "%Y-%m-%d %H:%M:%S")
    with freeze_time(time_string):
        refresh_token = User.objects.refresh_token(user=user, token=token)
        assert orig_key == refresh_token.key
        assert token.key is not None

    current = datetime.datetime.utcnow() + datetime.timedelta(hours=25)
    time_string = datetime.datetime.strftime(current, "%Y-%m-%d %H:%M:%S")
    with freeze_time(time_string):
        refresh_token = User.objects.refresh_token(user=user, token=token)
        assert orig_key != refresh_token.key
        assert token.key is None
