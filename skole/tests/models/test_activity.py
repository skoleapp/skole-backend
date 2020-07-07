from pytest import fixture

from skole.models import Activity, User


def test_str(db: fixture) -> None:
    user = User.objects.get(pk=2)
    description = "test description"
    test_activity = Activity.objects.create(user=user, description=description)
    assert str(test_activity) == description
