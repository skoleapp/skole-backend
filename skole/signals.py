from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from skole.models import Activity, Comment
from skole.utils.constants import ActivityDescriptions


# Create activities for comment replies, course and resource comments.
@receiver(post_save, sender=Comment)
def create_activity(
    sender: Comment, instance: Comment, created: bool, **kwargs: Any
) -> None:
    if created:
        target_user = instance.user

        # Reply comment.
        if instance.comment and instance.comment.user != target_user:
            Activity.objects.create(
                user=instance.comment.user,
                target_user=target_user,
                course=instance.comment.course,
                resource=instance.comment.resource,
                comment=instance.comment,
                description=ActivityDescriptions.COMMENT_REPLY,
            )

        # Course comment.
        elif instance.course and instance.course.user != target_user:
            Activity.objects.create(
                user=instance.course.user,
                target_user=target_user,
                course=instance.course,
                resource=None,
                comment=instance,
                description=ActivityDescriptions.COURSE_COMMENT,
            )

        # Resource comment.
        elif instance.resource and instance.resource.user != target_user:
            Activity.objects.create(
                user=instance.resource.user,
                target_user=target_user,
                course=None,
                resource=instance.resource,
                comment=instance,
                description=ActivityDescriptions.RESOURCE_COMMENT,
            )
