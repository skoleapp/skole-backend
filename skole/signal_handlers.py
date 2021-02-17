from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from skole.models import Activity, ActivityType, Comment
from skole.utils.constants import ActivityTypes
from skole.utils.email import send_email_notification


@receiver(post_save, sender=Comment)
def create_activity(
    sender: Comment, instance: Comment, created: bool, raw: bool, **kwargs: Any
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
    ):
        # Reply comment.
        Activity.objects.create(
            user=instance.comment.user,
            target_user=target_user,
            course=instance.comment.course,
            resource=instance.comment.resource,
            comment=instance.comment,
            activity_type=ActivityType.objects.get(name=ActivityTypes.COMMENT_REPLY),
        )
    else:
        if (
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
                comment=instance,
                activity_type=ActivityType.objects.get(
                    name=ActivityTypes.COURSE_COMMENT
                ),
            )

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
                comment=instance,
                activity_type=ActivityType.objects.get(
                    name=ActivityTypes.RESOURCE_COMMENT
                ),
            )


@receiver(post_save, sender=Activity)
def send_activity_email(
    sender: Activity, instance: Activity, created: bool, raw: bool, **kwargs: Any
) -> None:
    """Send email notification for new activities."""

    if not created or raw:
        # Skip when installing fixtures or when updating an activity.
        return

    kwargs = {
        "user": instance.user,
        "target_user": instance.target_user,
        "description": instance.activity_type.description,
    }

    # Reply comment.
    if instance.comment and instance.user.comment_reply_email_permission:
        send_email_notification(**kwargs)
    else:
        # Course comment.
        if instance.course and instance.user.course_comment_email_permission:
            send_email_notification(**kwargs)

        # Resource comment.
        if instance.resource and instance.user.resource_comment_email_permission:
            send_email_notification(**kwargs)
