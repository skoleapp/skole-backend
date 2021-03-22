from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import get_language

from skole.models import Activity, User
from skole.types import JsonDict, ResolveInfo
from skole.utils.constants import Notifications, TokenAction
from skole.utils.exceptions import UserAlreadyVerified
from skole.utils.token import get_token


def _get_frontend_url(*, add_lang: bool = False) -> str:
    if add_lang and (active := get_language()) != settings.LANGUAGE_CODE:
        lang = f"/{active}"
    else:
        lang = ""

    site = Site.objects.get_current()
    protocol = "http" if settings.DEBUG else "https"

    return f"{protocol}://{site.domain}{lang}"


def _send_templated_mail(
    subject: str,
    template: str,
    context: JsonDict,
    from_email: Optional[str] = None,
    user: Optional[User] = None,
    recipient_list: Optional[list[str]] = None,
) -> None:
    html_message = render_to_string(template_name=template, context=context)
    message = strip_tags(html_message)

    from_email = from_email if from_email is not None else settings.EMAIL_ADDRESS
    recipient_list = [user.email] if user else recipient_list or []

    if len(recipient_list) == 0:
        raise ValueError("Email has no recipients!")

    send_mail(
        subject=subject,
        from_email=from_email,
        message=message,
        html_message=html_message,
        recipient_list=recipient_list,
        fail_silently=False,
    )


def _get_auth_email_context(
    user: User, info: ResolveInfo, path: str, action: str, **kwargs: JsonDict
) -> JsonDict:
    token = get_token(user, action, **kwargs)

    url = f"{_get_frontend_url(add_lang=True)}/{path}?token={token}"

    return {"user": user, "url": url}


def send_verification_email(user: User, info: ResolveInfo) -> None:
    if user.verified:
        raise UserAlreadyVerified

    email_context = _get_auth_email_context(
        user, info, settings.VERIFICATION_PATH_ON_EMAIL, TokenAction.VERIFICATION
    )

    _send_templated_mail(
        subject=Notifications.VERIFY_ACCOUNT_SUBJECT,
        template="email/verify_account.html",
        context=email_context,
        user=user,
    )


def send_password_reset_email(user: User, info: ResolveInfo, recipient: str) -> None:
    email_context = _get_auth_email_context(
        user, info, settings.PASSWORD_RESET_PATH_ON_EMAIL, TokenAction.PASSWORD_RESET
    )

    _send_templated_mail(
        subject=Notifications.RESET_PASSWORD_SUBJECT,
        user=user,
        template="email/reset_password.html",
        context=email_context,
        recipient_list=[recipient],
    )


def send_comment_email_notification(activity: Activity) -> None:
    assert activity.comment

    causing_username = (
        activity.causing_user.username
        if activity.causing_user
        else Notifications.COMMUNITY_USER
    )

    activity_type = activity.activity_type
    activity_type.set_current_language(settings.LANGUAGE_CODE)
    description = activity_type.description

    subject = Notifications.COMMENT_EMAIL_NOTIFICATION_SUBJECT.format(
        causing_username, description
    )

    user = activity.user
    comment = activity.comment

    assert comment

    top_level_comment = comment.comment
    resource = comment.resource or getattr(top_level_comment, "resource", None)
    course = comment.course or getattr(top_level_comment, "course", None)
    school = comment.school or getattr(top_level_comment, "school", None)

    if resource or top_level_comment and top_level_comment.resource:
        path = settings.RESOURCE_COMMENT_PATH_ON_EMAIL.format(resource.slug, comment.pk)

    elif course or top_level_comment and top_level_comment.course:
        path = settings.COURSE_COMMENT_PATH_ON_EMAIL.format(course.slug, comment.pk)

    elif school or top_level_comment and top_level_comment.school:
        path = settings.SCHOOL_COMMENT_PATH_ON_EMAIL.format(school.slug, comment.pk)

    else:
        raise ValueError("Invalid activity. Cannot send email.")

    url = f"{_get_frontend_url()}/{path}"

    context = {
        "user": user,
        "causing_username": causing_username,
        "description": description,
        "url": url,
        "unsubscribe_url": f"{_get_frontend_url()}/{settings.ACCOUNT_SETTINGS_PATH_ON_EMAIL}",
    }

    _send_templated_mail(
        subject=subject,
        user=user,
        template="email/comment_email_notification.html",
        context=context,
    )


def send_badge_email_notification(activity: Activity) -> None:
    assert activity.badge_progress

    badge = activity.badge_progress.badge
    badge.set_current_language(settings.LANGUAGE_CODE)

    path = f"{settings.USER_PROFILE_PATH_ON_EMAIL.format(activity.user.slug)}"

    context = {
        "user": activity.user,
        "badge": badge,
        "url": f"{_get_frontend_url()}/{path}",
        "unsubscribe_url": f"{_get_frontend_url()}/{settings.ACCOUNT_SETTINGS_PATH_ON_EMAIL}",
    }

    _send_templated_mail(
        subject=Notifications.BADGE_EMAIL_NOTIFICATION_TITLE,
        template="email/badge_email_notification.html",
        user=activity.user,
        context=context,
    )
