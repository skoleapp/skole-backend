from __future__ import annotations

from django.apps import AppConfig


class SkoleAppConfig(AppConfig):
    name = "skole"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        import skole.patched  # noqa: F401 pylint: disable=import-outside-toplevel,unused-import
        import skole.signal_handlers  # noqa: F401 pylint: disable=import-outside-toplevel
