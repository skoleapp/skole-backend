from pytest import fixture

from core.models import User


def test_str(user: fixture) -> None:
    assert str(user) == "testuser"


def test_create_superuser(db: fixture) -> None:
    user = User.objects.create_superuser(email="root@root.com", username="root", password="root")
    assert user.is_superuser
    assert user.is_staff
    assert str(user) == "root"


def test_set_password(db: fixture, user: fixture) -> None:
    new_pass = "new pass"
    user = User.objects.set_password(user, new_pass)
    assert user.check_password(new_pass)
