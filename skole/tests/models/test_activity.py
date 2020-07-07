from pytest import fixture

from skole.models import Activity, User


def test_str(db: fixture) -> None:
    user = User.objects.get(pk=2)
    description = "test description"

    # Activity with a target user.
    target_user = User.objects.get(pk=3)
    test_activity = Activity.objects.create(
        user=user, target_user=target_user, description=description
    )
    assert str(test_activity) == f"{target_user.username} {description}"

    # Activity with no target user.
    test_activity2 = Activity.objects.create(user=user, description=description)
    assert str(test_activity2) == description
