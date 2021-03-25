from __future__ import annotations

from django.db import models

from skole.models.base import SkoleModel


class MarketingEmailSender(SkoleModel):
    from_email = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.from_email}"
