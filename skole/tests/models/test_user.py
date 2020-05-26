from pytest import fixture

from skole.models import School, Subject, User


def test_str(db: fixture) -> None:
    user2 = User.objects.get(pk=2)
    assert str(user2) == "testuser2"

    user3 = User.objects.get(pk=3)
    assert str(user3) == "testuser3"


def test_create_user(db: fixture) -> None:
    username = "testusername"
    email = "test@email.com"
    password = "password"
    school = School.objects.get(pk=1)
    subject = Subject.objects.get(pk=1)

    user = User.objects.create_user(
        username=username,
        email=email,
        school=school,
        subject=subject,
        password=password,
    )

    assert not user.is_staff
    assert not user.is_superuser
    assert user.username == username
    assert user.email == email
    assert user.school == school
    assert user.subject == subject
    assert user.check_password(password)


def test_create_superuser(db: fixture) -> None:
    username = "testadmin"
    email = "test@admin.com"
    password = "testpassword"
    user = User.objects.create_superuser(
        username=username, email=email, password=password
    )

    assert user.is_superuser
    assert user.is_staff
    assert user.username == username
    assert user.check_password(password)


def test_update_user(db: fixture) -> None:
    user = User.objects.get(pk=2)
    username = "newusername"
    email = "new@email.com"
    title = "new title"
    bio = "new bio"
    avatar = ""
    school = School.objects.get(pk=1)
    subject = Subject.objects.get(pk=1)

    User.objects.update_user(
        user=user,
        email=email,
        username=username,
        title=title,
        bio=bio,
        avatar=avatar,
        school=school,
        subject=subject,
    )

    assert user.username == username
    assert user.email == email
    assert user.title == title
    assert user.bio == bio
    assert user.avatar == avatar
    assert user.school == school
    assert user.subject == subject


def test_set_password(db: fixture) -> None:
    user = User.objects.get(pk=2)
    new_pass = "new pass"
    User.objects.set_password(user, new_pass)
    assert user.check_password(new_pass)


def test_change_score(db: fixture) -> None:
    user = User.objects.get(pk=2)
    assert user.score == 0

    # Increment.
    User.objects.change_score(user=user, score=1)
    assert user.score == 1

    # Decrement
    User.objects.change_score(user=user, score=-1)
    assert user.score == 0


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


def test_rank(db: fixture) -> None:
    testuser2 = User.objects.get(pk=2)
    assert testuser2.rank == "Freshman"

    testuser3 = User.objects.get(pk=3)
    assert testuser3.rank == "Tutor"

    testuser4 = User.objects.get(pk=4)
    assert testuser4.rank == "Mentor"

    testuser5 = User.objects.get(pk=5)
    assert testuser5.rank == "Master"

    testuser6 = User.objects.get(pk=6)
    assert testuser6.rank == "Doctor"

    testuser7 = User.objects.get(pk=7)
    assert testuser7.rank == "Professor"
