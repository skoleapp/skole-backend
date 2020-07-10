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
    # Skip when installing fixtures.
    if created and not raw:
        target_user = instance.user

        # Reply comment.
        if instance.comment and instance.comment.user != target_user:
            comment_reply = ActivityType.objects.get(pk=1)
            assert comment_reply.name == ActivityTypes.COMMENT_REPLY
            user = cast(User, instance.comment.user)

            Activity.objects.create(
                user=user,
                target_user=target_user,
                course=instance.comment.course,
                resource=instance.comment.resource,
                comment=instance.comment,
                activity_type=comment_reply,
            )

        # Course comment.
        elif instance.course and instance.course.user != target_user:
            course_comment = ActivityType.objects.get(pk=2)
            assert course_comment.name == ActivityTypes.COURSE_COMMENT
            user = cast(User, instance.course.user)

            Activity.objects.create(
                user=user,
                target_user=target_user,
                course=instance.course,
                resource=None,
                comment=instance,
                activity_type=course_comment,
            )

        # Resource comment.
        elif instance.resource and instance.resource.user != target_user:
            resource_comment = ActivityType.objects.get(pk=3)
            assert resource_comment.name == ActivityTypes.RESOURCE_COMMENT
            user = cast(User, instance.resource.user)

            Activity.objects.create(
                user=user,
                target_user=target_user,
                course=None,
                resource=instance.resource,
                comment=instance,
                activity_type=resource_comment,
            )
