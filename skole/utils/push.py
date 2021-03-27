from django.conf import settings
from fcm_django.models import FCMDevice

from skole.models import Activity, User
from skole.types import JsonDict
from skole.utils.constants import Notifications


def _send_push_notification(user: User, title: str, body: str, data: JsonDict) -> None:
    try:
        fcm_device = FCMDevice.objects.get(user=user)
    except FCMDevice.DoesNotExist:
        pass
    else:
        fcm_device.send_message(title=title, body=body, data=data)


def send_comment_push_notification(activity: Activity) -> None:
    causing_username = (
        activity.causing_user.username
        if activity.causing_user
        else Notifications.COMMUNITY_USER
    )

    comment = activity.comment
    assert comment

    if top_level_comment := comment.comment:
        resource_slug = getattr(top_level_comment.resource, "slug", None)
        thread_slug = getattr(top_level_comment.thread, "slug", None)
        school_slug = getattr(top_level_comment.school, "slug", None)

    else:
        resource_slug = getattr(comment.resource, "slug", None)
        thread_slug = getattr(comment.thread, "slug", None)
        school_slug = getattr(comment.school, "slug", None)

    activity_type = activity.activity_type
    activity_type.set_current_language(settings.LANGUAGE_CODE)
    title = Notifications.COMMENT_PUSH_NOTIFICATION_TITLE
    body = f"{causing_username} {activity_type.description}."

    data = {
        "activity": activity.pk,
        "resource": resource_slug,
        "thread": thread_slug,
        "school": school_slug,
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
