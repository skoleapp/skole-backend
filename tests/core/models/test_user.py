from pytest import fixture

from core.models import User


def test_str(db: fixture) -> None:
    user2 = User.objects.get(pk=2)
    assert str(user2) == "testuser2"

    user3 = User.objects.get(pk=3)
    assert str(user3) == "testuser3"


def test_create_user(db: fixture) -> None:
    username = "testusername"
    email = "test@email.com"
    password = "password"
    user = User.objects.create_user(username=username, email=email, password=password)

    assert not user.is_staff
    assert not user.is_superuser
    assert user.username == username
    assert user.email == ""
    assert user.check_password(password)


def test_create_superuser(db: fixture) -> None:
    username = "testroot"
    password = "testpassword"
    user = User.objects.create_superuser(username=username, password=password)

    assert user.is_superuser
    assert user.is_staff
    assert user.username == username
    assert user.check_password(password)


def test_update_user(db: fixture) -> None:
    user = User.objects.get(pk=2)
    email = "new@email.com"
    username = "newusername"
    title = "new title"
    bio = "new bio"
    avatar = ""
    User.objects.update_user(
        user=user, email=email, username=username, title=title, bio=bio, avatar=avatar,
    )

    assert user.email == email
    assert user.username == username
    assert user.title == title
    assert user.bio == bio
    assert user.avatar == avatar


def test_set_password(db: fixture) -> None:
    user = User.objects.get(pk=2)
    new_pass = "new pass"
    User.objects.set_password(user, new_pass)

    assert user.check_password(new_pass)
