from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from skole.models import Badge, User
from skole.signal_handlers import BadgeSignalHandler


class _UserHolder:
    def __init__(self, user: User) -> None:
        self.user = user


class Command(BaseCommand):
    """Retroactively award all users with all badges that they have earned."""

    def handle(self, *args: Any, **options: Any) -> None:
        for signal_handler in BadgeSignalHandler.__subclasses__():
            badge = Badge.objects.get(identifier=signal_handler.identifier)
            if not badge.made_available:
                for user in get_user_model().objects.iterator():
                    signal_handler.update_progress(
                        # Ignore: For convenience we pass these dumb values here.
                        sender=object,  # type: ignore[type-var]
                        instance=_UserHolder(user),
                        created=True,
                        raw=False,
                    )
                badge.made_available = True
                badge.save(update_fields=("made_available",))
