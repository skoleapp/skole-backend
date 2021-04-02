import pytest

from skole.models import ActivityType


@pytest.mark.django_db
def test_str() -> None:
    comment_reply = ActivityType.objects.get(pk=1)
    assert str(comment_reply) == "comment_reply"

    thread_comment = ActivityType.objects.get(pk=2)
    assert str(thread_comment) == "thread_comment"

    new_badge = ActivityType.objects.get(pk=4)
    assert str(new_badge) == "new_badge"
