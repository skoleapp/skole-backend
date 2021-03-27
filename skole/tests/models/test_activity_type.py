import pytest

from skole.models import ActivityType


@pytest.mark.django_db
def test_str() -> None:
    comment_reply = ActivityType.objects.get(pk=1)
    assert str(comment_reply) == "comment_reply"

    thread_comment = ActivityType.objects.get(pk=2)
    assert str(thread_comment) == "thread_comment"

    resource_comment = ActivityType.objects.get(pk=3)
    assert str(resource_comment) == "resource_comment"
