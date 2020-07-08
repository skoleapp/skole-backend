from pytest import fixture

from skole.models import Activity, ActivityType, User


def test_str(db: fixture) -> None:
    user = User.objects.get(pk=2)
    activity_type = ActivityType.objects.get(pk=1)
    test_activity = Activity.objects.create(user=user, activity_type=activity_type)
    assert str(test_activity) == str(activity_type)
