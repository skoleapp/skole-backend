import pytest
from pytest import fixture

from skole.models import Activity, Comment, Course, User
from skole.utils.constants import Activities


def test_activity_for_comment_reply(db: fixture) -> None:
    testuser2 = User.objects.get(pk=2)

    # Test that activity is created if a user replies to a comment created by some other user.
    comment = Comment.objects.get(pk=4)  # Created by testuser2
    comment_reply = Comment.objects.get(
        pk=12
    )  # Reply comment to the comment above, created by testuser3.
    Activity.objects.get(
        user=comment.user,
        target_user=comment_reply.user,
        translations__description=Activities.COMMENT_REPLY,
    )  # Throws error if it doesn't exist.

    # Test that activity is not created if user replies to his own comment.
    own_reply_comment = Comment.objects.create_comment(
        user=testuser2, text="test", target=comment, attachment=None
    )

    # Ignore: comment is an optional union attribute to a comment so it might not have the 'user' defined.
    # In this case we now that this comment targets another comment, however.
    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=own_reply_comment.comment.user, target_user=own_reply_comment.user)  # type: ignore[union-attr]


def test_activity_for_course_comment(db: fixture) -> None:
    course = Course.objects.get(pk=1)

    # Test that activity is created if a user comments on a course created by some other user.
    comment = Comment.objects.get(
        pk=9
    )  # Comment created by testuser3, targeted to the course above.
    Activity.objects.get(
        user=course.user,
        target_user=comment.user,
        translations__description=Activities.COURSE_COMMENT,
    )  # Throws error if it doesn't exist.

    # Test that activity is not created if user comments his own course.
    own_course_comment = Comment.objects.get(
        pk=8
    )  # Comment created by testuser2, targeted to his own course.

    # Ignore: comment is an optional union attribute to a comment so it might not have the 'user' defined.
    # In this case we now that this comment targets another comment, however.
    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=own_course_comment.course.user, target_user=own_course_comment.user)  # type: ignore[union-attr]


def test_activity_for_resource_comment(db: fixture) -> None:
    resource = Course.objects.get(pk=1)

    # Test that activity is created if a user comments on a resource created by some other user.
    comment = Comment.objects.get(
        pk=2
    )  # Comment created by testuser3, targeted to the resource above.
    Activity.objects.get(
        user=resource.user,
        target_user=comment.user,
        translations__description=Activities.RESOURCE_COMMENT,
    )  # Throws error if it doesn't exist.

    # Test that activity is not created if user comments his own resource.
    own_resource_comment = Comment.objects.get(
        pk=1
    )  # Comment created by testuser2, targeted to his own resource.

    # Ignore: comment is an optional union attribute to a comment so it might not have the 'user' defined.
    # In this case we now that this comment targets another comment, however.
    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=own_resource_comment.resource.user, target_user=own_resource_comment.user)  # type: ignore[union-attr]
