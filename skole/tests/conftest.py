import random
import shutil
import tempfile
from collections.abc import Generator

import django.core.cache
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.test import override_settings
from pytest import fixture

from skole.types import Fixture


@fixture(scope="session")
def django_db_setup(  # pylint: disable=redefined-outer-name
    django_db_setup: Fixture,
    django_db_blocker: Fixture,
) -> None:
    """Setup the database and load the test data that is used in all tests."""

    with django_db_blocker.unblock():
        # Install the Postgres extension that allows to use `TrigramSimilarity` func.
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

        call_command(
            "loaddata",
            ["test-data.yaml", "initial-activity-types.yaml", "initial-badges.yaml"],
        )


@fixture(scope="session", autouse=True)
def no_api_keys() -> Generator[None, None, None]:
    """We really really do not want to call the API during tests."""
    with override_settings(CLOUDMERSIVE_API_KEY=None):
        yield


@fixture(scope="session", autouse=True)
def seed_random_generator() -> Generator[None, None, None]:
    """Make sure that random numbers generated during tests are always predictable."""
    random.seed(0)
    yield


@fixture(scope="session", autouse=True)
def temp_media() -> Generator[None, None, None]:
    """Make all created test media be temporary."""
    temp_media_dir = tempfile.mkdtemp()

    # Make sure that the 3 test files are available for opening in the temp folder.
    shutil.copytree(settings.MEDIA_ROOT, temp_media_dir, dirs_exist_ok=True)

    with override_settings(MEDIA_ROOT=temp_media_dir):
        yield
    shutil.rmtree(temp_media_dir, ignore_errors=True)


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
