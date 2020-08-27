import shutil
import tempfile
from typing import Generator

from django.conf import settings
from django.core.management import call_command
from pytest import fixture

from skole.utils.types import Fixture


def pytest_configure(config: Fixture) -> None:
    # We really really do not want to call the API during tests.
    settings.CLOUDMERSIVE_API_KEY = None


@fixture(scope="session")
def django_db_setup(django_db_setup: Fixture, django_db_blocker: Fixture) -> None:
    """Load test data fixtures for all non-class based tests as well."""
    with django_db_blocker.unblock():
        call_command("loaddata", "test-data.yaml")


@fixture(scope="session", autouse=True)
def temp_media() -> Generator[None, None, None]:
    """Make all created test media be temporary."""
    temp_media = tempfile.mkdtemp()
    settings.MEDIA_ROOT = temp_media
    yield
    shutil.rmtree(temp_media, ignore_errors=True)
