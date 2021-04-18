from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import get_language

from skole.models import Activity, User
from skole.types import JsonDict
from skole.utils.constants import Notifications, TokenAction
from skole.utils.exceptions import BackupEmailAlreadyVerified, UserAlreadyVerified
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

    if recipient_list is not None and user is not None:
        raise ValueError("You cannot provide both the `recipient_list` and the `user`.")

    if recipient_list is None and user is not None:
        recipient_list = [user.email]
        if user.backup_email and user.verified_backup_email:
            recipient_list.append(user.backup_email)

    if not recipient_list:
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
    user: User, path: str, action: str, **kwargs: JsonDict
) -> JsonDict:
    token = get_token(user, action, **kwargs)

    url = f"{_get_frontend_url(add_lang=True)}/{path}?token={token}"

    return {"user": user, "url": url}


def send_verification_email(user: User) -> None:
    if user.verified:
        raise UserAlreadyVerified

    email_context = _get_auth_email_context(
        user, settings.VERIFICATION_PATH_ON_EMAIL, TokenAction.VERIFICATION
    )

    _send_templated_mail(
        subject=Notifications.VERIFY_ACCOUNT_SUBJECT,
        template="email/verify_account.html",
        context=email_context,
        # Don't pass the `user` here since the verification email shouldn't go to the
        # backup email.
        recipient_list=[user.email],
    )


def send_backup_email_verification_email(user: User) -> None:
    if user.verified_backup_email:
        raise BackupEmailAlreadyVerified

    email_context = _get_auth_email_context(
        user,
        settings.BACKUP_EMAIL_VERIFICATION_PATH_ON_EMAIL,
        TokenAction.BACKUP_EMAIL_VERIFICATION,
    )

    _send_templated_mail(
        subject=Notifications.VERIFY_BACKUP_EMAIL_SUBJECT,
        template="email/verify_backup_email.html",
        context=email_context | {"backup_email": user.backup_email},
        # The primary email needs to be the one that verifies the backup email.
        recipient_list=[user.email],
    )


def send_password_reset_email(user: User, recipient: str) -> None:
    email_context = _get_auth_email_context(
        user, settings.PASSWORD_RESET_PATH_ON_EMAIL, TokenAction.PASSWORD_RESET
    )

    _send_templated_mail(
        subject=Notifications.RESET_PASSWORD_SUBJECT,
        template="email/reset_password.html",
        context=email_context,
        recipient_list=[recipient],
    )


def send_comment_email_notification(activity: Activity) -> None:
    assert activity.comment

    causing_username = (
        activity.causing_user.username
        if activity.causing_user
        else Notifications.ANONYMOUS_STUDENT
    )

    activity_type = activity.activity_type
    activity_type.set_current_language(settings.LANGUAGE_CODE)

    # Will be in the middle of a sentence.
    description = activity_type.description.rstrip(".")

    subject = Notifications.COMMENT_EMAIL_NOTIFICATION_SUBJECT.format(
        causing_username, description
    )

    user = activity.user
    comment = activity.comment

    assert comment

    top_level_comment = comment.comment
    thread = comment.thread or getattr(top_level_comment, "thread", None)

    if thread or top_level_comment and top_level_comment.thread:
        path = settings.THREAD_COMMENT_PATH_ON_EMAIL.format(thread.slug, comment.pk)
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
