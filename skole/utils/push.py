from django.core.exceptions import ObjectDoesNotExist
from fcm_django.models import FCMDevice

from skole.models import Activity
from skole.utils.constants import Email


def send_push_notification(activity: Activity) -> None:
    target_username = (
        activity.target_user.username if activity.target_user else Email.COMMUNITY_USER
    )

    description = activity.activity_type.description
    title = Email.PUSH_NOTIFICATION_TITLE
    body = f"{target_username} {description}."

    data = {
        "activity": activity.pk,
        "course": getattr(activity.course, "slug", None),
        "resource": getattr(activity.resource, "slug", None),
        "school": getattr(activity.school, "slug", None),
        "comment": getattr(activity.comment, "pk", None),
    }

    try:
        fcm_device = FCMDevice.objects.get(user=activity.user)

    except ObjectDoesNotExist:
        pass

    else:
        fcm_device.send_message(title=title, body=body, data=data)
