import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from skole.models import Activity, ActivityType, BadgeProgress, Comment
from skole.utils.constants import ActivityTypes
from skole.utils.email import (
    send_badge_email_notification,
    send_comment_email_notification,
)
from skole.utils.push import (
    send_badge_push_notification,
    send_comment_push_notification,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Comment)
def create_activity_from_comment(
    sender: type[Comment], instance: Comment, created: bool, raw: bool, **kwargs: Any
) -> None:
    """Create activity for course comment, resource comment, or comment reply."""

    # Skip when installing fixtures or when updating a comment.
    if not created or raw:
        return

    causing_user = instance.user
    top_level_comment = instance.comment
    resource = instance.resource
    course = instance.course

    # Skip when replying to anonymous comment.
    if top_level_comment and not top_level_comment.user:
        return

    # Skip when replying to own comment.
    if top_level_comment and causing_user == top_level_comment.user:
        return

    # Skip when commenting on own resource.
    if resource and causing_user == resource.user:
        return

    # Skip when commenting on own course.
    if course and causing_user == course.user:
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
        activity_type = ActivityType.objects.get(
            identifier=ActivityTypes.RESOURCE_COMMENT
        )

        Activity.objects.create(
            user=user,
            causing_user=causing_user,
            comment=instance,
            activity_type=activity_type,
        )

    if course:
        # If the comment is sent to both a resource and a course that share the same owner, only create an activity for the resource comment.
        if not resource or resource and resource.user != course.user:
            activity_type = ActivityType.objects.get(
                identifier=ActivityTypes.COURSE_COMMENT
            )

            Activity.objects.create(
                user=user,
                causing_user=causing_user,
                comment=instance,
                activity_type=activity_type,
            )

    elif top_level_comment:
        activity_type = ActivityType.objects.get(identifier=ActivityTypes.COMMENT_REPLY)

        Activity.objects.create(
            user=user,
            causing_user=causing_user,
            comment=instance,
            activity_type=activity_type,
        )


@receiver(post_save, sender=BadgeProgress)
def create_activity_from_badge(
    sender: type[BadgeProgress],
    instance: BadgeProgress,
    created: bool,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Create activity when a user acquires a badge."""

    if raw:
        # Skip when installing fixtures.
        return

    # The value can be `None` but still be in the dict.
    update_fields = kwargs.get("update_fields") or {}

    if not instance.acquired or "acquired" not in update_fields:
        # Only notify once after acquiring the badge. `BadgeProgress.save` makes sure
        # that `acquired` is in `update_fields` the time that the badge is first
        # acquired. It shouldn't be put to `update_fields` anywhere else.
        return

    Activity.objects.create(
        user=instance.user,
        badge_progress=instance,
        activity_type=ActivityType.objects.get(identifier=ActivityTypes.NEW_BADGE),
    )


@receiver(post_save, sender=Activity)
def send_activity_notifications(  # pylint: disable=too-many-branches; (not so bad really)
    sender: type[Activity], instance: Activity, created: bool, raw: bool, **kwargs: Any
) -> None:
    """Send email and push notifications for new activities."""

    # Skip when installing fixtures or when updating an activity.
    if not created or raw:
        return

    user = instance.user

    if comment := instance.comment:
        if comment.resource:
            if user.resource_comment_email_permission:
                send_comment_email_notification(activity=instance)
            if user.resource_comment_push_permission:
                send_comment_push_notification(activity=instance)

        if comment.course:
            if user.course_comment_email_permission:
                send_comment_email_notification(activity=instance)
            if user.course_comment_push_permission:
                send_comment_push_notification(activity=instance)

        elif comment.comment:
            if user.comment_reply_email_permission:
                send_comment_email_notification(activity=instance)
            if user.comment_reply_push_permission:
                send_comment_push_notification(activity=instance)

    elif instance.badge_progress:
        if user.new_badge_email_permission:
            send_badge_email_notification(activity=instance)
        if user.new_badge_push_permission:
            send_badge_push_notification(activity=instance)

    logger.warning(f"Invalid activity: {instance!r} with no target.")
