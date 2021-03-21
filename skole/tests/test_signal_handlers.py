import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail

from skole.models import Activity, BadgeProgress, Comment, Course, Resource, User
from skole.utils.constants import Notifications


@pytest.mark.django_db
def test_activity_for_comment_reply() -> None:
    testuser2 = User.objects.get(pk=2)
    testuser3 = User.objects.get(pk=3)
    comment = Comment.objects.get(pk=5)  # Created by testuser2

    # Make sure activity does not exist.
    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(
            user=comment.user,
            causing_user=testuser3,
            comment=comment,
        )

    # Test that activity is created if another user replies to a comment.

    reply_comment = Comment.objects.create(
        user=testuser3, text="test", attachment=None, comment=comment
    )

    Activity.objects.get(
        user=comment.user,
        causing_user=reply_comment.user,
        comment=reply_comment,
    )

    # Test that activity is not created if user replies to his own comment.

    own_reply_comment = Comment.objects.create(
        user=testuser2, text="test", comment=comment, attachment=None
    )

    assert own_reply_comment.comment
    user = own_reply_comment.comment.user

    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=user, causing_user=own_reply_comment.user)

    # Test that activity is not created for replies on anonyous comments.

    course = Course.objects.get(pk=1)
    anonymous_top_level_comment = Comment.objects.create(
        user=None, text="test", course=course
    )
    reply_comment = Comment.objects.create(
        user=None, text="test", comment=anonymous_top_level_comment
    )

    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(comment=reply_comment)


@pytest.mark.django_db
def test_activity_for_course_comment() -> None:
    # Test that activity is created if a user comments on a course created by some other user.

    course = Course.objects.get(pk=1)
    testuser3 = User.objects.get(pk=3)
    assert course.user != testuser3

    comment = Comment.objects.create(
        user=testuser3, text="test", course=course, attachment=None
    )

    Activity.objects.get(
        user=course.user,
        causing_user=comment.user,
        comment=comment,
    )

    # Test that activity is not created if user comments his own course.

    testuser2 = User.objects.get(pk=2)
    assert course.user == testuser2

    own_course_comment = Comment.objects.create(
        user=testuser2, text="test", course=course, attachment=None
    )

    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(  # type: ignore[misc]
            user=own_course_comment.course.user, causing_user=own_course_comment.user  # type: ignore[union-attr]
        )


@pytest.mark.django_db
def test_activity_for_resource_comment() -> None:
    resource = Resource.objects.get(pk=1)
    testuser3 = User.objects.get(pk=3)

    comment = Comment.objects.create(
        user=testuser3, text="test", resource=resource, attachment=None
    )

    # Test that activity is created if a user comments on a resource created by some other user.

    assert comment.user != resource.user

    Activity.objects.get(
        user=resource.user,
        causing_user=comment.user,
        comment=comment,
    )

    # Test that activity is not created if user comments his own resource.

    testuser2 = User.objects.get(pk=2)

    own_resource_comment = Comment.objects.create(
        user=testuser2, text="test", resource=resource, attachment=None
    )

    assert resource.user == own_resource_comment.user

    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=resource.user, causing_user=own_resource_comment.user)


@pytest.mark.django_db
def test_activity_for_comment_on_multiple_discussions() -> None:
    # Test that if a comment is created on a resource and course with the same owner, an activity is created only for the resource comment.

    course = Course.objects.get(pk=1)
    resource = Resource.objects.get(pk=1)
    comment = Comment.objects.create(
        user=None, text="test", course=course, resource=resource
    )
    Activity.objects.get(comment=comment)

    # Test that if a comment is created on a resource and course with different owners, an activity is created for both of them.

    resource = Resource.objects.get(pk=2)
    comment = Comment.objects.create(
        user=None, text="test", course=course, resource=resource
    )
    assert Activity.objects.filter(comment=comment).count() == 2


@pytest.mark.django_db
def test_comment_email_notifications() -> None:
    # Test that email notifications are sent for resource comments.

    resource = Resource.objects.get(pk=1)
    resource_comment = Comment.objects.create(text="test", resource=resource)
    activity = Activity.objects.get(comment=resource_comment)
    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert sent.from_email == settings.EMAIL_ADDRESS
    assert sent.to == [activity.user.email]

    assert sent.subject == Notifications.COMMENT_EMAIL_NOTIFICATION_SUBJECT.format(
        Notifications.COMMUNITY_USER, activity.activity_type.description
    )

    # Test that email notifications are sent for course comments.

    course = Course.objects.get(pk=1)
    course_comment = Comment.objects.create(text="test", course=course)
    activity = Activity.objects.get(comment=course_comment)
    assert len(mail.outbox) == 2
    sent = mail.outbox[1]
    assert sent.from_email == settings.EMAIL_ADDRESS
    assert sent.to == [activity.user.email]

    assert sent.subject == Notifications.COMMENT_EMAIL_NOTIFICATION_SUBJECT.format(
        Notifications.COMMUNITY_USER, activity.activity_type.description
    )

    # Test that email notifications are sent for comment replies.

    course = Course.objects.get(pk=1)
    testuser2 = get_user_model().objects.get(pk=2)
    top_level_comment = Comment.objects.create(
        user=testuser2, text="test", course=course
    )
    assert len(mail.outbox) == 3  # 'First Comment' badge
    reply_comment = Comment.objects.create(text="test", comment=top_level_comment)
    activity = Activity.objects.get(comment=reply_comment)
    assert len(mail.outbox) == 4  # Comment activity
    sent = mail.outbox[3]
    assert sent.from_email == settings.EMAIL_ADDRESS
    assert sent.to == [activity.user.email]

    assert sent.subject == Notifications.COMMENT_EMAIL_NOTIFICATION_SUBJECT.format(
        Notifications.COMMUNITY_USER, activity.activity_type.description
    )

    # Test that email notifications are not sent without permission.

    user = get_user_model().objects.get(pk=11)
    course = Course.objects.get(pk=26)
    resource = Resource.objects.get(pk=16)
    assert course.user == user
    assert resource.user == user
    assert not user.resource_comment_email_permission
    assert not user.course_comment_email_permission
    assert not user.comment_reply_email_permission
    assert not user.new_badge_email_permission

    course_comment = Comment.objects.create(course=course, text="test")
    Activity.objects.get(comment=course_comment)

    resource_comment = Comment.objects.create(resource=resource, text="test")
    Activity.objects.get(comment=resource_comment)

    top_level_comment = Comment.objects.create(
        user=user, resource=resource, text="test"
    )
    reply_comment = Comment.objects.create(comment=top_level_comment, text="test")
    Activity.objects.get(comment=reply_comment)

    assert len(mail.outbox) == 4


@pytest.mark.django_db
def test_badge_email_notifications() -> None:
    assert len(mail.outbox) == 0

    progress = BadgeProgress.objects.get(pk=1)
    progress.save(update_fields=["acquired"])  # Resend the acquiring notification.
    assert len(mail.outbox) == 1
    progress.save()  # This does not send it again.
    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert "Badge" in sent.subject
    assert "Staff" in sent.body

    # No 'First Comment' badge for anonymous comments.
    Comment.objects.create(text="A comment.", course_id=2)
    assert len(mail.outbox) == 2
    sent = mail.outbox[1]
    assert "commented on your course" in sent.subject

    # No 'First Comment' badge for anonymous comments.
    Comment.objects.create(text="A comment.", course_id=2, user_id=2)
    assert len(mail.outbox) == 4
    sent = mail.outbox[2]
    assert "commented on your course" in sent.subject
    sent = mail.outbox[3]
    assert "Badge" in sent.subject
    assert "First Comment" in sent.body

    Course.objects.create(name="New Course", school_id=1, user_id=2)
    assert len(mail.outbox) == 5
    sent = mail.outbox[4]
    assert "Badge" in sent.subject
    assert "First Course" in sent.body
    assert "http://localhost:3001/users/testuser2" in sent.body


# @pytest.mark.django_db
# def test_push_notifications() -> None:
#     # TODO: Implement.
#     pass
