import pytest
from pytest import fixture

from skole.models import Activity, Comment, User


def test_activity_for_comment_reply(db: fixture) -> None:
    testuser2 = User.objects.get(pk=2)
    comment = Comment.objects.get(pk=4)  # Created by testuser2

    # Reply comment to the comment above, created by testuser3.
    comment_reply = Comment.objects.get(pk=12)

    # Test that activity is created if a user replies to a comment created by some other user.

    Activity.objects.get(
        user=comment.user,
        target_user=comment_reply.user,
        course=comment.course,
        resource=comment.resource,
        comment=comment,
    )

    # Test that activity is not created if user replies to his own comment.
    own_reply_comment = Comment.objects.create_comment(
        user=testuser2, text="test", target=comment, attachment=None
    )

    # Ignore: comment is an optional union attribute to a comment so it might not have the 'user' defined.
    # In this case we now that this comment targets another comment, however.
    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=own_reply_comment.comment.user, target_user=own_reply_comment.user)  # type: ignore[union-attr]


def test_activity_for_course_comment(db: fixture) -> None:
    # Comment created by testuser3, targeted to other user's course.
    comment = Comment.objects.get(pk=9)

    # Comment created by testuser2, targeted to his own course.
    own_course_comment = Comment.objects.get(pk=8)

    # Test that activity is created if a user comments on a course created by some other user.

    # Ignore: Course is an optional field to a comment, but we now that this comment is targeted a course in the fixtures.
    Activity.objects.get(
        user=comment.course.user,  # type: ignore[union-attr]
        target_user=comment.user,
        course=comment.course,
        resource=comment.resource,
        comment=comment,
    )

    # Test that activity is not created if user comments his own course.

    # Ignore: comment is an optional union attribute to a comment so it might not have the 'user' defined.
    # In this case we now that this comment targets another comment, however.
    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=own_course_comment.course.user, target_user=own_course_comment.user)  # type: ignore[union-attr]


def test_activity_for_resource_comment(db: fixture) -> None:
    # Comment created by testuser3, targeted to other user's course.
    comment = Comment.objects.get(pk=2)

    # Comment created by testuser2, targeted to his own resource.
    own_resource_comment = Comment.objects.get(pk=1)

    # Test that activity is created if a user comments on a resource created by some other user.

    # Ignore: Resource is an optional field to a comment, but we now that this comment is targeted a resource in the fixtures.
    Activity.objects.get(
        user=comment.resource.user,  # type: ignore[union-attr]
        target_user=comment.user,
        course=comment.course,
        resource=comment.resource,
        comment=comment,
    )

    # Test that activity is not created if user comments his own resource.

    # Ignore: comment is an optional union attribute to a comment so it might not have the 'user' defined.
    # In this case we now that this comment targets another comment, however.
    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=own_resource_comment.resource.user, target_user=own_resource_comment.user)  # type: ignore[union-attr]
