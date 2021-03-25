from __future__ import annotations

from django.db import models

from skole.models.base import SkoleModel
from skole.utils.constants import MARKETING_EMAIL_TYPE_CHOICES


class MarketingEmail(SkoleModel):
    """Models one marketing email sent out to subscribers."""

    subject = models.CharField(max_length=150)
    from_email = models.ForeignKey(
        "skole.MarketingEmailSender", on_delete=models.SET_NULL, null=True
    )
    email_type = models.CharField(max_length=50, choices=MARKETING_EMAIL_TYPE_CHOICES)
    contents = models.FileField(upload_to="marketing_emails")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    sent = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.subject}"
