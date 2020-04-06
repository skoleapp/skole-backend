from django.contrib.auth import get_user_model
from pytest import fixture


def test_str(db: fixture) -> None:
    user2 = get_user_model().objects.get(pk=2)
    assert str(user2) == "testuser2"

    user3 = get_user_model().objects.get(pk=3)
    assert str(user3) == "testuser3"


def test_create_user(db: fixture) -> None:
    username = "testusername"
    password = "password"
    user = get_user_model().objects.create_user(username=username, password=password)

    assert not user.is_staff
    assert not user.is_superuser
    assert user.username == username
    assert user.email == ""
    assert user.check_password(password)


def test_create_superuser(db: fixture) -> None:
    username = "testroot"
    password = "testpassword"
    user = get_user_model().objects.create_superuser(
        username=username, password=password
    )

    assert user.is_superuser
    assert user.is_staff
    assert user.username == username
    assert user.check_password(password)


def test_update_user(db: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    email = "new@email.com"
    username = "newusername"
    title = "new title"
    bio = "new bio"
    avatar = ""
    get_user_model().objects.update_user(
        user=user, email=email, username=username, title=title, bio=bio, avatar=avatar,
    )

    assert user.email == email
    assert user.username == username
    assert user.title == title
    assert user.bio == bio
    assert user.avatar == avatar


def test_set_password(db: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    new_pass = "new pass"
    get_user_model().objects.set_password(user, new_pass)

    assert user.check_password(new_pass)
