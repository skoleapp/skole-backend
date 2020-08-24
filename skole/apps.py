from django.apps import AppConfig


class SkoleAppConfig(AppConfig):
    name = "skole"

    def ready(self) -> None:
        import skole.patched  # noqa
        import skole.signal_handlers  # noqa
