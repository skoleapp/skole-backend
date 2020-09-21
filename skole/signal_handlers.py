from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from skole.models import Activity, ActivityType, Comment
from skole.utils.constants import ActivityTypes


# Create activities for comment replies, course and resource comments.
@receiver(post_save, sender=Comment)
def create_activity(
    sender: Comment, instance: Comment, created: bool, raw: bool, **kwargs: Any
) -> None:
    """Create activity for course comment, resource comment, or comment reply."""

    if not created or raw:
        # Skip when installing fixtures or when updating a comment.
        return

    target_user = instance.user

    if instance.comment:
        if instance.comment.user and instance.comment.user != target_user:
            Activity.objects.create(
                user=instance.comment.user,
                target_user=target_user,
                course=instance.comment.course,
                resource=instance.comment.resource,
                comment=instance.comment,
                activity_type=ActivityType.objects.get(
                    name=ActivityTypes.COMMENT_REPLY
                ),
            )
    elif instance.course:
        if instance.course.user and instance.course.user != target_user:
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
    elif instance.resource:
        if instance.resource.user and instance.resource.user != target_user:
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
