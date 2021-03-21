import pytest

from skole.models import ActivityType


@pytest.mark.django_db
def test_clear_cache_setup() -> None:
    a = ActivityType.objects.get(pk=1)
    assert a.identifier == "comment_reply"
    assert a.description == "replied to your comment"
    a.identifier = "new identifier"
    a.description = "new description"
    a.save()
    a.refresh_from_db()
    assert a.identifier == "new identifier"
    assert a.description == "new description"


@pytest.mark.django_db
def test_clear_cache_test() -> None:
    """Without `conftest.clear_cache` autouse fixture, this testcase would fail."""
    a = ActivityType.objects.get(pk=1)
    assert a.identifier == "comment_reply"

    # Would fetch "new description" from cache and fail on this line.
    assert a.description == "replied to your comment"
