from skole.models import ActivityType
from skole.types import Fixture


def test_clear_cache_setup(db: Fixture) -> None:
    a = ActivityType.objects.get(pk=1)
    assert a.name == "comment_reply"
    assert a.description == "replied to your comment."
    a.name = "new name"
    a.description = "new description"
    a.save()
    a.refresh_from_db()
    assert a.name == "new name"
    assert a.description == "new description"


def test_clear_cache_test(db: Fixture) -> None:
    """Without `conftest.clear_cache` autouse fixture, this testcase would fail."""
    a = ActivityType.objects.get(pk=1)
    assert a.name == "comment_reply"

    # Would fetch "new description" from cache and fail on this line.
    assert a.description == "replied to your comment."
