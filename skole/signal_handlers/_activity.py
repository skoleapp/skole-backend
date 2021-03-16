from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from skole.models import Activity, ActivityType, Comment
from skole.utils.constants import ActivityTypes
from skole.utils.email import send_email_notification
from skole.utils.push import send_push_notification


@receiver(post_save, sender=Comment)
def create_activity(
    sender: type[Comment], instance: Comment, created: bool, raw: bool, **kwargs: Any
) -> None:
    """Create activity for course comment, resource comment, or comment reply."""

    # Skip when installing fixtures or when updating a comment.
    if not created or raw:
        return

    target_user = instance.user
    top_level_comment = instance.comment
    resource = instance.resource
    course = instance.course

    # Skip when replying to anonymous comment.
    if top_level_comment and not top_level_comment.user:
        return

    # Skip when replying to own comment.
    if top_level_comment and target_user == top_level_comment.user:
        return

    # Skip when commenting on own resource.
    if resource and target_user == resource.user:
        return

    # Skip when commenting on own course.
    if course and target_user == course.user:
        return

    # The user receiving the activity is one of the following:
    # - Owner of the resource.
    # - Owner of the course.
    # - Owner of the top-level comment.
    user = (
        getattr(resource, "user", None)
        or getattr(course, "user", None)
        or getattr(top_level_comment, "user", None)
    )

    if resource:
        activity_type = ActivityType.objects.get(name=ActivityTypes.RESOURCE_COMMENT)

        Activity.objects.create(
            user=user,
            target_user=target_user,
            comment=instance,
            activity_type=activity_type,
        )

    if course:
        # If the comment is sent to both a resource and a course that share the same owner, only create an activity for the resource comment.
        if not resource or resource and resource.user != course.user:
            activity_type = ActivityType.objects.get(name=ActivityTypes.COURSE_COMMENT)

            Activity.objects.create(
                user=user,
                target_user=target_user,
                comment=instance,
                activity_type=activity_type,
            )

    elif top_level_comment:
        activity_type = ActivityType.objects.get(name=ActivityTypes.COMMENT_REPLY)

        Activity.objects.create(
            user=user,
            target_user=target_user,
            comment=instance,
            activity_type=activity_type,
        )


@receiver(post_save, sender=Activity)
def send_activity_notifications(
    sender: type[Activity], instance: Activity, created: bool, raw: bool, **kwargs: Any
) -> None:
    """Send email and push notifications for new activities."""

    # Skip when installing fixtures or when updating an activity.
    if not created or raw:
        return

    comment = instance.comment

    # Skip if activity is invalid.
    if not comment:
        return

    user = instance.user
    resource = comment.resource
    course = comment.course

    if resource:
        if user.resource_comment_email_permission:
            send_email_notification(activity=instance)
        if user.resource_comment_push_permission:
            send_push_notification(activity=instance)

    if course:
        if user.course_comment_email_permission:
            send_email_notification(activity=instance)
        if user.course_comment_push_permission:
            send_push_notification(activity=instance)

    elif comment.comment:
        if user.comment_reply_email_permission:
            send_email_notification(activity=instance)
        if user.comment_reply_push_permission:
            send_push_notification(activity=instance)
