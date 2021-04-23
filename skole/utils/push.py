import logging

from django.conf import settings
from fcm_django.models import FCMDevice
from pyfcm.errors import FCMError

from skole.models import Activity, User
from skole.types import JsonDict
from skole.utils.constants import Notifications

logger = logging.getLogger(__name__)


def _send_push_notification(user: User, title: str, body: str, data: JsonDict) -> None:
    for fcm_device in FCMDevice.objects.filter(user=user):
        try:
            fcm_device.send_message(title=title, body=body, data=data)
        except FCMError as e:
            logger.error(e)


def send_comment_push_notification(activity: Activity) -> None:
    causing_username = (
        activity.causing_user.username
        if activity.causing_user
        else Notifications.ANONYMOUS_STUDENT
    )

    comment = activity.comment
    assert comment

    if top_level_comment := comment.comment:
        thread_slug = getattr(top_level_comment.thread, "slug", None)
    else:
        thread_slug = getattr(comment.thread, "slug", None)

    activity_type = activity.activity_type
    activity_type.set_current_language(settings.LANGUAGE_CODE)
    title = Notifications.COMMENT_PUSH_NOTIFICATION_TITLE
    body = f"{causing_username} {activity_type.description}"

    data = {
        "activity": activity.pk,
        "thread": thread_slug,
        "comment": comment.pk,
    }

    _send_push_notification(user=activity.user, title=title, body=body, data=data)


def send_badge_push_notification(activity: Activity) -> None:
    badge_progress = activity.badge_progress
    assert badge_progress
    badge = badge_progress.badge
    badge.set_current_language(settings.LANGUAGE_CODE)
    title = Notifications.BADGE_PUSH_NOTIFICATION_TITLE
    body = Notifications.BADGE_PUSH_NOTIFICATION_BODY.format(badge)

    data = {
        "activity": activity.pk,
        "user": badge_progress.user.slug,
    }

    _send_push_notification(user=activity.user, title=title, body=body, data=data)
