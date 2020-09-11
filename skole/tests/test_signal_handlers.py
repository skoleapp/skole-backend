from typing import cast

import pytest

from skole.models import Activity, Comment, Course, Resource, User
from skole.types import Fixture


def test_activity_for_comment_reply(db: Fixture) -> None:
    testuser2 = User.objects.get(pk=2)
    testuser3 = User.objects.get(pk=3)
    comment = Comment.objects.get(pk=4)  # Created by testuser2

    # Reply comment to the comment above, created by testuser3.
    reply_comment = Comment.objects.create(
        user=testuser3, text="test", attachment=None, comment=comment
    )

    # Test that activity is created if a user replies to a comment created by some other user.

    Activity.objects.get(
        user=comment.user,
        target_user=reply_comment.user,
        course=comment.course,
        resource=comment.resource,
        comment=comment,
    )

    # Test that activity is not created if user replies to his own comment.
    own_reply_comment = Comment.objects.create(
        user=testuser2, text="test", comment=comment, attachment=None
    )

    # Ignore: comment is an optional union attribute to a comment so it might not have the 'user' defined.
    #   In this case we now that this comment targets another comment, however.

    # Ignore: Mypy thinks that the comment is optional but we now that this comment is attached to another comment.
    user = cast(User, own_reply_comment.comment.user)

    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=user, target_user=own_reply_comment.user)


def test_activity_for_course_comment(db: Fixture) -> None:
    # Not created by testuser 3.
    course = Course.objects.get(pk=1)
    testuser3 = User.objects.get(pk=3)
    comment = Comment.objects.create(
        user=testuser3, text="test", course=course, attachment=None
    )

    # Test that activity is created if a user comments on a course created by some other user.

    # Ignore: Mypy thinks that the course is optional but we now that this comment is attached to a course.
    user = cast(User, comment.course.user)

    # Ignore: Course is an optional field to a comment, but we now that this comment is targeted a course in the fixtures.
    Activity.objects.get(
        user=user,
        target_user=comment.user,
        course=comment.course,
        resource=comment.resource,
        comment=comment,
    )

    # Test that activity is not created if user comments his own course.

    testuser2 = User.objects.get(pk=2)
    own_course_comment = Comment.objects.create(
        user=testuser2, text="test", course=course, attachment=None
    )

    # Ignore 1: Mypy thinks that the course is optional but we now that this comment is attached to a course.
    user = cast(User, own_course_comment.course.user)
    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=user, target_user=own_course_comment.user)


def test_activity_for_resource_comment(db: Fixture) -> None:
    resource = Resource.objects.get(pk=1)
    testuser3 = User.objects.get(pk=3)
    comment = Comment.objects.create(
        user=testuser3, text="test", resource=resource, attachment=None
    )

    # Test that activity is created if a user comments on a resource created by some other user.

    # Ignore: Mypy thinks that the resource is optional but we now that this comment is attached to a resource.
    user = cast(User, comment.resource.user)

    Activity.objects.get(
        user=user,
        target_user=comment.user,
        course=comment.course,
        resource=comment.resource,
        comment=comment,
    )

    # Test that activity is not created if user comments his own resource.

    testuser2 = User.objects.get(pk=2)
    own_resource_comment = Comment.objects.create(
        user=testuser2, text="test", resource=resource, attachment=None
    )

    # Ignore 1: Mypy thinks that the resource is optional but we now that this comment is attached to a resource.
    user = cast(User, own_resource_comment.resource.user)
    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=user, target_user=own_resource_comment.user)
