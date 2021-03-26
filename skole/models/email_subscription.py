from __future__ import annotations

from typing import Optional

from django.db import models

from skole.models.base import SkoleManager, SkoleModel
from skole.utils.constants import TokenAction, ValidationErrors, VerboseNames
from skole.utils.token import get_token_payload


class EmailSubscriptionManager(SkoleManager["EmailSubscription"]):
    def update_email_subscription(
        self,
        token: str,
        product_updates: bool,
        blog_posts: bool,
    ) -> tuple[Optional[EmailSubscription], bool]:
        payload = get_token_payload(token, TokenAction.UPDATE_EMAIL_SUBSCRIPTION)
        obj = self.get(**payload)
        deleted = False

        # Delete instance when user unsubscribes from everything.
        if not product_updates and not blog_posts:
            obj.delete()
            # Ignore: `None` type cannot be assigned to instance of type `EmailSubscription` without Mypy error.
            obj = None  # type: ignore[assignment]
            deleted = True
        else:
            obj.product_updates = product_updates
            obj.blog_posts = blog_posts
            obj.save(update_fields=["product_updates", "blog_posts"])

        return obj, deleted


class EmailSubscription(SkoleModel):
    """Models one email subscription by an anonymous user."""

    email = models.EmailField(
        VerboseNames.EMAIL,
        unique=True,
        error_messages={"unique": ValidationErrors.EMAIL_ALREADY_SUBSCRIBED},
    )

    product_updates = models.BooleanField(default=True)
    blog_posts = models.BooleanField(default=True)

    objects = EmailSubscriptionManager()

    def __str__(self) -> str:
        return f"{self.email}"
