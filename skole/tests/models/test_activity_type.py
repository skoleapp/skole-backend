from pytest import fixture

from skole.models import ActivityType


def test_str(db: fixture) -> None:
    comment_reply = ActivityType.objects.get(pk=1)
    assert str(comment_reply) == "comment_reply"

    course_comment = ActivityType.objects.get(pk=2)
    assert str(course_comment) == "course_comment"

    resource_comment = ActivityType.objects.get(pk=3)
    assert str(resource_comment) == "resource_comment"
