from skole.models import User
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    user2 = User.objects.get(pk=2)
    assert str(user2) == "testuser2"

    user3 = User.objects.get(pk=3)
    assert str(user3) == "testuser3"


def test_set_password(db: Fixture) -> None:
    user = User.objects.get(pk=2)
    new_pass = "new pass"
    User.objects.set_password(user, new_pass)
    assert user.check_password(new_pass)


def test_change_score(db: Fixture) -> None:
    user = User.objects.get(pk=2)
    assert user.score == 0

    # Increment.
    User.objects.change_score(user=user, score=1)
    assert user.score == 1

    # Decrement
    User.objects.change_score(user=user, score=-1)
    assert user.score == 0


def test_rank(db: Fixture) -> None:
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


# def test_verify_user() -> None:
#     # TODO: Implement.
#     pass
#
#
# def test_send_verification_email() -> None:
#     # TODO: Implement.
#     pass
#
#
# def test_resend_verification_email() -> None:
#     # TODO: Implement.
#     pass
#
#
# def test_send_password_reset_email() -> None:
#     # TODO: Implement.
#     pass
