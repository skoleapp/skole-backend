from core.models import User


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
