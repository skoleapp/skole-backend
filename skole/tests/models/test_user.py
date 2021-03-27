import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from fcm_django.models import FCMDevice

from skole.models import Badge, BadgeProgress, User


@pytest.mark.django_db
def test_str() -> None:
    user2 = User.objects.get(pk=2)
    assert str(user2) == "testuser2"

    user3 = User.objects.get(pk=3)
    assert str(user3) == "testuser3"


@pytest.mark.django_db
def test_create_user() -> None:
    username = "testusername"
    email = "username@test.test"
    password = "password"

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )

    assert not user.is_staff
    assert not user.is_superuser
    assert user.username == username
    assert user.email == email
    assert user.check_password(password)
    # Email notification permission are by default off.
    assert not user.comment_reply_email_permission
    assert not user.thread_comment_email_permission
    assert not user.new_badge_email_permission

    # Push notification permission are by default on.
    assert user.comment_reply_push_permission
    assert user.thread_comment_push_permission
    assert user.new_badge_push_permission

    user = User.objects.create_user(
        username="unique",
        email="unique@test.test",
        password=password,
    )


@pytest.mark.django_db
def test_create_superuser() -> None:
    username = "testadmin"
    email = "newadmin@test.test"
    password = "adminpassword"
    user = User.objects.create_superuser(
        username=username, email=email, password=password
    )

    assert user.is_superuser
    assert user.is_staff
    assert user.username == username
    assert user.check_password(password)


@pytest.mark.django_db
def test_set_password() -> None:
    user = User.objects.get(pk=2)
    new_pass = "new pass"
    User.objects.set_password(user, new_pass)
    assert user.check_password(new_pass)


@pytest.mark.django_db
def test_change_score() -> None:
    user = User.objects.get(pk=2)
    assert user.score == 0

    # Increment.
    user.change_score(1)
    assert user.score == 1

    # Decrement
    user.change_score(-1)
    assert user.score == 0


@pytest.mark.django_db
def test_rank() -> None:
    testuser2 = User.objects.get(pk=2)
    assert testuser2.rank == "Freshman"

    testuser3 = User.objects.get(pk=3)
    assert testuser3.rank == "Tutor"

    testuser4 = User.objects.get(pk=4)
    assert testuser4.rank == "Mentor"

    testuser5 = User.objects.get(pk=5)
    assert testuser5.rank == "Bachelor"

    testuser6 = User.objects.get(pk=6)
    assert testuser6.rank == "Master"

    testuser7 = User.objects.get(pk=7)
    assert testuser7.rank == "Doctor"

    testuser8 = User.objects.get(pk=8)
    assert testuser8.rank == "Professor"

    testuser9 = User.objects.get(pk=9)
    assert testuser9.score == 0 and testuser9.rank == "Freshman"


@pytest.mark.django_db
def test_get_or_create_badge_progresses() -> None:
    user = get_user_model().objects.get(pk=10)
    assert Badge.objects.filter(steps__isnull=False).count() == 4
    assert BadgeProgress.objects.filter(user=user).count() == 0

    badge_progresses = user.get_or_create_badge_progresses()

    assert badge_progresses.count() == 4
    assert BadgeProgress.objects.filter(user=user).count() == 4

    badge_progress = badge_progresses.order_by("pk")[0]
    assert badge_progress.badge.identifier == "first_comment"
    assert badge_progress.badge.steps == 1
    assert badge_progress.progress == 0
    assert badge_progress.acquired is None


@pytest.mark.django_db
def test_change_selected_badge_progress() -> None:
    user = get_user_model().objects.get(pk=10)
    assert user.selected_badge_progress is None

    badge_progress = user.change_selected_badge_progress(Badge.objects.get(pk=2))
    user.refresh_from_db()
    # Ignore: We know that `badge` cannot be `None` here.
    assert user.selected_badge_progress.badge.pk == 2  # type: ignore[attr-defined]
    assert badge_progress.badge.pk == 2


# @pytest.mark.django_db
# def test_register_verify_user() -> None:
#     TODO: Implement.
#     pass


@pytest.mark.django_db
def test_register_fcm_token() -> None:
    user = get_user_model().objects.get(pk=2)

    with pytest.raises(ObjectDoesNotExist):
        FCMDevice.objects.get(user=user)

    # Register new token.

    token = "token"
    user.register_fcm_token(token=token)
    assert FCMDevice.objects.count() == 1
    FCMDevice.objects.get(user=user, registration_id=token)

    # Register a second device.

    token = "token2"
    user.register_fcm_token(token=token)
    assert FCMDevice.objects.count() == 2
    FCMDevice.objects.get(user=user, registration_id=token)

    # Update existing token.

    token = "token2"
    user.register_fcm_token(token=token)
    assert FCMDevice.objects.count() == 2
    FCMDevice.objects.get(user=user, registration_id=token)
