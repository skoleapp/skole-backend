from typing import Any, cast

from django.db.models.signals import post_save
from django.dispatch import receiver

from skole.models import Activity, ActivityType, Comment, User
from skole.utils.constants import ActivityTypes


# Create activities for comment replies, course and resource comments.
@receiver(post_save, sender=Comment)
def create_activity(
    sender: Comment, instance: Comment, created: bool, raw: bool, **kwargs: Any
) -> None:
    # Skip when installing fixtures or when the target doesn't have a user.
    if created and not raw and instance.user:
        target_user = instance.user

        if instance.comment and instance.comment.user != target_user:
            Activity.objects.create(
                user=cast(User, instance.comment.user),
                target_user=target_user,
                course=instance.comment.course,
                resource=instance.comment.resource,
                comment=instance.comment,
                activity_type=ActivityType.objects.get(
                    name=ActivityTypes.COMMENT_REPLY
                ),
            )
        elif instance.course and instance.course.user != target_user:
            Activity.objects.create(
                user=cast(User, instance.course.user),
                target_user=target_user,
                course=instance.course,
                resource=None,
                comment=instance,
                activity_type=ActivityType.objects.get(
                    name=ActivityTypes.COURSE_COMMENT
                ),
            )
        elif instance.resource and instance.resource.user != target_user:
            Activity.objects.create(
                user=cast(User, instance.resource.user),
                target_user=target_user,
                course=None,
                resource=instance.resource,
                comment=instance,
                activity_type=ActivityType.objects.get(
                    name=ActivityTypes.RESOURCE_COMMENT
                ),
            )
