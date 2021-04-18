import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail

from skole.models import Activity, BadgeProgress, Comment, Thread, User


@pytest.mark.django_db
def test_activity_for_comment_reply() -> None:
    user2 = User.objects.get(pk=2)
    user3 = User.objects.get(pk=3)
    comment = Comment.objects.get(pk=5)  # Created by testuser2

    # Make sure activity does not exist.
    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(
            user=comment.user,
            causing_user=user3,
            comment=comment,
        )

    # Test that activity is created if another user replies to a comment.

    reply_comment = Comment.objects.create(user=user3, text="test", comment=comment)

    Activity.objects.get(
        user=comment.user,
        causing_user=reply_comment.user,
        comment=reply_comment,
    )

    # Test that activity is not created if user replies to his own comment.

    own_reply_comment = Comment.objects.create(user=user2, text="test", comment=comment)

    assert own_reply_comment.comment
    user = own_reply_comment.comment.user

    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(user=user, causing_user=own_reply_comment.user)

    # Test that activity is not created for replies on anonyous comments.

    thread = Thread.objects.get(pk=1)
    anonymous_top_level_comment = Comment.objects.create(
        user=None, text="test", thread=thread
    )
    reply_comment = Comment.objects.create(
        user=None, text="test", comment=anonymous_top_level_comment
    )

    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(comment=reply_comment)


@pytest.mark.django_db
def test_activity_for_thread_comment() -> None:
    # Test that activity is created if a user comments on a thread created by some other user.

    thread = Thread.objects.get(pk=1)
    user3 = User.objects.get(pk=3)
    assert thread.user != user3

    comment = Comment.objects.create(user=user3, text="test", thread=thread)

    Activity.objects.get(
        user=thread.user,
        causing_user=comment.user,
        comment=comment,
    )

    # Test that activity is not created if user comments his own thread.

    user2 = User.objects.get(pk=2)
    assert thread.user == user2

    own_thread_comment = Comment.objects.create(user=user2, text="test", thread=thread)

    with pytest.raises(Activity.DoesNotExist):
        Activity.objects.get(  # type: ignore[misc]
            user=own_thread_comment.thread.user, causing_user=own_thread_comment.user  # type: ignore[union-attr]
        )


@pytest.mark.django_db
def test_comment_email_notifications() -> None:
    # Test that email notifications are sent for thread comments.

    thread = Thread.objects.get(pk=1)
    user2 = thread.user
    assert user2
    user2.comment_reply_email_permission = True
    user2.thread_comment_email_permission = True
    user2.save()

    thread_comment = Comment.objects.create(text="test", thread=thread)
    activity = Activity.objects.get(comment=thread_comment)
    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert sent.from_email == settings.EMAIL_ADDRESS
    assert sent.to == [activity.user.email]

    assert sent.subject == "Anonymous Student commented on your thread in Skole"

    # Test that email notifications are sent for comment replies.

    thread = Thread.objects.get(pk=1)
    user2 = get_user_model().objects.get(pk=2)
    top_level_comment = Comment.objects.create(user=user2, text="test", thread=thread)
    reply_comment = Comment.objects.create(text="test", comment=top_level_comment)
    activity = Activity.objects.get(comment=reply_comment)
    assert len(mail.outbox) == 2
    sent = mail.outbox[1]
    assert sent.from_email == settings.EMAIL_ADDRESS
    assert sent.to == [activity.user.email]

    assert sent.subject == "Anonymous Student replied to your comment in Skole"

    # Test that email notifications are not sent without permission.

    user11 = get_user_model().objects.get(pk=11)
    thread = Thread.objects.get(pk=26)
    assert thread.user == user11

    assert not user11.thread_comment_email_permission
    assert not user11.comment_reply_email_permission
    assert not user11.new_badge_email_permission
    user2.thread_comment_email_permission = False
    user2.comment_reply_email_permission = False
    user2.new_badge_email_permission = False
    user2.save()

    thread_comment = Comment.objects.create(user=user2, thread=thread, text="test")
    Activity.objects.get(comment=thread_comment)

    reply_comment = Comment.objects.create(comment=thread_comment, text="test")
    Activity.objects.get(comment=reply_comment)

    assert len(mail.outbox) == 2


@pytest.mark.django_db
def test_badge_email_notifications() -> None:
    assert len(mail.outbox) == 0

    progress = BadgeProgress.objects.get(pk=1)
    user = progress.user
    user.new_badge_email_permission = True
    user.save()

    progress.save(update_fields=["acquired"])  # Resend the acquiring notification.
    assert len(mail.outbox) == 1
    progress.save()  # This does not send it again.
    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert "Badge" in sent.subject
    assert "Staff" in sent.body

    # No 'First Comment' badge for anonymous comments.
    Comment.objects.create(text="A comment.", thread_id=2)
    assert len(mail.outbox) == 1

    # Gets 'First Comment' badge for creating a comment.
    Comment.objects.create(text="A comment.", thread_id=2, user_id=2)
    assert len(mail.outbox) == 2
    sent = mail.outbox[1]
    assert "Badge" in sent.subject
    assert "First Comment" in sent.body
    assert "http://localhost:3001/users/testuser2" in sent.body

    # Gets 'First Thread' badge for creating a thread.
    Thread.objects.create(title="New Thread", user_id=2)
    assert len(mail.outbox) == 3
    sent = mail.outbox[2]
    assert "Badge" in sent.subject
    assert "First Thread" in sent.body
    assert "http://localhost:3001/users/testuser2" in sent.body


# @pytest.mark.django_db
# def test_push_notifications() -> None:
#     # TODO: Implement.
#     pass
