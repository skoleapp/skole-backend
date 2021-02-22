from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.core.mail import get_connection, send_mail
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import get_language

from skole.models import EmailSubscription, MarketingEmail, User
from skole.types import JsonDict, ResolveInfo
from skole.utils.constants import Email, MarketingEmailTypes, TokenAction
from skole.utils.exceptions import UserAlreadyVerified
from skole.utils.token import get_token


def _send(
    subject: str,
    from_email: str,
    template: str,
    context: JsonDict,
    user: Optional[User] = None,
    recipient_list: Optional[list[str]] = None,
) -> None:
    html_message = render_to_string(template_name=template, context=context)
    message = strip_tags(html_message)
    recipient_list = [user.email] if user else recipient_list or []

    if len(recipient_list) == 0:
        raise ValueError("Email is missing recipients!")

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
    site = get_current_site(info.context)
    protocol = "http" if settings.DEBUG else "https"

    if (active := get_language()) != settings.LANGUAGE_CODE:
        lang = f"{active}/"
    else:
        lang = ""

    url = f"{protocol}://{site.domain}/{lang}{path}?token={token}"

    return {"user": user, "url": url}


def send_verification_email(user: User, info: ResolveInfo) -> None:
    if user.verified:
        raise UserAlreadyVerified

    email_context = _get_auth_email_context(
        user, info, settings.VERIFICATION_PATH_ON_EMAIL, TokenAction.VERIFICATION
    )

    return _send(
        subject=Email.VERIFY_ACCOUNT_SUBJECT,
        from_email=settings.EMAIL_ADDRESS,
        template="email/verify_account.html",
        context=email_context,
        user=user,
    )


def send_password_reset_email(user: User, info: ResolveInfo, recipient: str) -> None:
    email_context = _get_auth_email_context(
        user, info, settings.PASSWORD_RESET_PATH_ON_EMAIL, TokenAction.PASSWORD_RESET
    )

    return _send(
        subject=Email.RESET_PASSWORD_SUBJECT,
        from_email=settings.EMAIL_ADDRESS,
        template="email/reset_password.html",
        user=user,
        context=email_context,
        recipient_list=[recipient],
    )


# Create dynamic unsubscription link - link registered users to their account settings and create a token for others.
def _get_marketing_email_context(
    request: HttpRequest, email: str, contents: str
) -> JsonDict:
    protocol = "http" if settings.DEBUG else "https"
    site = get_current_site(request)

    if get_user_model().objects.filter(email=email).exists():
        path = settings.ACCOUNT_SETTINGS_PATH_ON_EMAIL
        update_email_subscription_url = f"{protocol}://{site.domain}/{path}"
    else:
        path = settings.UPDATE_EMAIL_SUBSCRIPTION_PATH_ON_EMAIL
        payload = {"email": email, "action": TokenAction.UPDATE_EMAIL_SUBSCRIPTION}
        token = signing.dumps(payload)

        update_email_subscription_url = (
            f"{protocol}://{site.domain}/{path}?token={token}"
        )

    return {
        "contents": contents,
        "update_email_subscription_url": update_email_subscription_url,
    }


def send_marketing_email(request: HttpRequest, instance: MarketingEmail) -> None:
    if instance.email_type == MarketingEmailTypes.PRODUCT_UPDATE:
        user_emails = (
            get_user_model()
            .objects.filter(product_update_email_permission=True)
            .values_list("email", flat=True)
        )

        subscriber_emails = EmailSubscription.objects.filter(
            product_updates=True
        ).values_list("email", flat=True)

    if instance.email_type == MarketingEmailTypes.BLOG_POST:
        user_emails = (
            get_user_model()
            .objects.filter(blog_post_email_permission=True)
            .values_list("email", flat=True)
        )

        subscriber_emails = EmailSubscription.objects.filter(
            blog_posts=True
        ).values_list("email", flat=True)

    recipient_list = user_emails.union(subscriber_emails)
    contents = instance.contents.read().decode("utf-8")

    with get_connection():
        for recipient in recipient_list.iterator():
            _send(
                subject=instance.subject,
                from_email=str(instance.from_email),
                template="email/marketing_email.html",
                context=_get_marketing_email_context(
                    request=request, email=recipient, contents=contents
                ),
                recipient_list=[recipient],
            )


def _get_email_notification_context(
    user: User, target_username: str, description: str
) -> JsonDict:
    site = Site.objects.get_current()
    protocol = "http" if settings.DEBUG else "https"
    path = settings.ACTIVITY_PATH_ON_EMAIL
    url = f"{protocol}://{site.domain}/{path}"

    return {
        "user": user,
        "target_username": target_username,
        "description": description,
        "url": url,
    }


def send_email_notification(
    user: User, description: str, target_user: Optional[User] = None
) -> None:
    target_username = target_user.username if target_user else Email.COMMUNITY_USER
    subject = Email.EMAIL_NOTIFICATION_SUBJECT.format(target_username, description)
    email_context = _get_email_notification_context(
        user=user, target_username=target_username, description=description
    )

    return _send(
        subject=subject,
        from_email=settings.EMAIL_ADDRESS,
        template="email/email_notification.html",
        user=user,
        context=email_context,
    )
