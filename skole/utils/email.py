from __future__ import annotations

from typing import List, Optional

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from skole.models import User
from skole.types import JsonDict, ResolveInfo
from skole.utils.constants import Email, TokenAction
from skole.utils.exceptions import UserAlreadyVerified
from skole.utils.token import get_token


def _send(
    subject: str,
    template: str,
    context: JsonDict,
    user: User,
    recipient_list: Optional[List[str]] = None,
) -> None:
    html_message = render_to_string(template, context)
    message = strip_tags(html_message)

    send_mail(
        subject=subject,
        from_email=settings.EMAIL_NO_REPLY,
        message=message,
        html_message=html_message,
        recipient_list=(recipient_list or [user.email]),
        fail_silently=False,
    )


def _get_auth_email_context(
    user: User, info: ResolveInfo, path: str, action: str, **kwargs: JsonDict
) -> JsonDict:
    token = get_token(user, action, **kwargs)
    site = get_current_site(info.context)
    protocol = "http" if settings.DEBUG else "https"

    url = f"{protocol}://{site.domain}/{path}?token={token}"

    return {"user": user, "url": url}


def send_verification_email(user: User, info: ResolveInfo) -> None:
    email_context = _get_auth_email_context(
        user, info, settings.VERIFICATION_PATH_ON_EMAIL, TokenAction.VERIFICATION
    )
    return _send(
        subject=Email.VERIFY_ACCOUNT_SUBJECT,
        template=settings.EMAIL_TEMPLATE_VERIFICATION,
        context=email_context,
        user=user,
    )


def resend_verification_email(user: User, info: ResolveInfo) -> None:
    if user.verified:
        raise UserAlreadyVerified

    email_context = _get_auth_email_context(
        user, info, settings.VERIFICATION_PATH_ON_EMAIL, TokenAction.VERIFICATION
    )
    return _send(
        subject=Email.VERIFY_ACCOUNT_SUBJECT,
        template=settings.EMAIL_TEMPLATE_VERIFICATION,
        user=user,
        context=email_context,
    )


def send_password_reset_email(user: User, info: ResolveInfo, recipient: str) -> None:
    email_context = _get_auth_email_context(
        user, info, settings.PASSWORD_RESET_PATH_ON_EMAIL, TokenAction.PASSWORD_RESET
    )
    return _send(
        subject=Email.RESET_PASSWORD_SUBJECT,
        template=settings.EMAIL_TEMPLATE_PASSWORD_RESET,
        user=user,
        context=email_context,
        recipient_list=[recipient],
    )
