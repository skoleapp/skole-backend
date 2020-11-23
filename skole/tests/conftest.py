import shutil
import tempfile
from typing import Generator

import django.core.cache
from django.conf import settings
from django.core.management import call_command
from django.test import override_settings
from pytest import fixture

from skole.types import Fixture


@fixture(scope="session")
def django_db_setup(  # pylint: disable=redefined-outer-name
    django_db_setup: Fixture,
    django_db_blocker: Fixture,
) -> None:
    """Load test data fixtures for all non-class based tests as well."""
    with django_db_blocker.unblock():
        call_command("loaddata", "test-data.yaml")


@fixture(scope="session", autouse=True)
def no_api_keys() -> Generator[None, None, None]:
    """We really really do not want to call the API during tests."""
    with override_settings(CLOUDMERSIVE_API_KEY=None):
        yield


@fixture(scope="session", autouse=True)
def temp_media() -> Generator[None, None, None]:
    """Make all created test media be temporary."""
    media_directory = tempfile.mkdtemp()
    settings.MEDIA_ROOT = media_directory
    yield
    shutil.rmtree(media_directory, ignore_errors=True)


@fixture(scope="function", autouse=True)
def clear_cache() -> Generator[None, None, None]:
    """
    Clear the cache after every test.

    This surprisingly is not (at least yet) the default behavior:
    https://code.djangoproject.com/ticket/11505

    Without this, changes to translated fields of a model would persist between
    test cases, since parler prefers to fetch the translated fields from the cache.
    """
    yield
    django.core.cache.cache.clear()
