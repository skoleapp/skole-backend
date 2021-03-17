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

    if not created or raw:
        # Skip when installing fixtures or when updating a comment.
        return

    target_user = instance.user

    if (
        instance.comment
        and instance.comment.user
        and instance.comment.user != target_user
        and not instance.comment.comment
    ):
        # Reply comment.
        Activity.objects.create(
            user=instance.comment.user,
            target_user=target_user,
            course=instance.comment.course,
            resource=instance.comment.resource,
            school=instance.comment.school,
            comment=instance.comment,
            activity_type=ActivityType.objects.get(name=ActivityTypes.COMMENT_REPLY),
        )
    else:
        if (
            instance.resource
            and instance.resource.user
            and instance.resource.user != target_user
        ):
            # Resource comment.
            Activity.objects.create(
                user=instance.resource.user,
                target_user=target_user,
                course=None,
                resource=instance.resource,
                school=None,
                comment=instance,
                activity_type=ActivityType.objects.get(
                    name=ActivityTypes.RESOURCE_COMMENT
                ),
            )

        elif (
            instance.course
            and instance.course.user
            and instance.course.user != target_user
        ):
            # Course comment.
            Activity.objects.create(
                user=instance.course.user,
                target_user=target_user,
                course=instance.course,
                resource=None,
                school=None,
                comment=instance,
                activity_type=ActivityType.objects.get(
                    name=ActivityTypes.COURSE_COMMENT
                ),
            )


@receiver(post_save, sender=Activity)
def send_activity_email(
    sender: type[Activity], instance: Activity, created: bool, raw: bool, **kwargs: Any
) -> None:
    """Send email notification for new activities."""

    if not created or raw:
        # Skip when installing fixtures or when updating an activity.
        return

    # Reply comment.
    if instance.comment:
        if instance.user.comment_reply_email_permission:
            send_email_notification(activity=instance)
        if instance.user.comment_reply_push_permission:
            send_push_notification(activity=instance)

    # Resource comment.
    elif instance.resource:
        if instance.user.resource_comment_email_permission:
            send_email_notification(activity=instance)
        if instance.user.resource_comment_push_permission:
            send_push_notification(activity=instance)

    # Course comment.
    elif instance.course:
        if instance.user.course_comment_email_permission:
            send_email_notification(activity=instance)
        if instance.user.course_comment_push_permission:
            send_push_notification(activity=instance)
