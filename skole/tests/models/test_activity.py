from skole.models import Activity, ActivityType, User
from skole.utils.types import Fixture


def test_str(db: Fixture) -> None:
    testuser2 = User.objects.get(pk=2)
    activity_type = ActivityType.objects.get(pk=1)
    test_activity = Activity.objects.create(user=testuser2, activity_type=activity_type)
    assert str(test_activity) == str(activity_type)
    test_activity.delete()


def test_mark_read(db: Fixture) -> None:
    testuser2 = User.objects.get(pk=2)
    activity_type = ActivityType.objects.get(pk=1)
    test_activity = Activity.objects.create(user=testuser2, activity_type=activity_type)
    assert not test_activity.read

    # Test marking an activity as read.
    test_activity = Activity.objects.mark_read(activity=test_activity, read=True)
    assert test_activity.read

    # Test marking an activity as not read.
    test_activity = Activity.objects.mark_read(activity=test_activity, read=False)
    assert not test_activity.read

    test_activity.delete()


def test_mark_all_as_read(db: Fixture) -> None:
    testuser2 = User.objects.get(pk=2)
    activity_type = ActivityType.objects.get(pk=1)
    test_activity1 = Activity.objects.create(
        user=testuser2, activity_type=activity_type
    )
    test_activity2 = Activity.objects.create(
        user=testuser2, activity_type=activity_type
    )

    assert not test_activity1.read
    assert not test_activity1.read

    Activity.objects.mark_all_as_read(user=testuser2)

    test_activity1.refresh_from_db()
    test_activity2.refresh_from_db()

    assert test_activity1.read
    assert test_activity2.read

    test_activity1.delete()
    test_activity2.delete()
