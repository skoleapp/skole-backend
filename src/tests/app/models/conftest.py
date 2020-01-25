import shutil
import tempfile
from typing import Generator

from django.conf import settings
from django.core.management import call_command
from pytest import fixture


@fixture(scope="session")
def django_db_setup(django_db_setup: fixture, django_db_blocker: fixture) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", "test-data.yaml")


@fixture
def temp_media() -> Generator[None, None, None]:
    """Use this fixture to make all created media be temporary.
    Reference: https://www.caktusgroup.com/blog/2013/06/26/media-root-and-django-tests/
    """
    settings._original_media_root = settings.MEDIA_ROOT
    settings._original_file_storage = settings.DEFAULT_FILE_STORAGE
    _temp_media = tempfile.mkdtemp()
    settings.MEDIA_ROOT = _temp_media
    settings.DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    yield
    shutil.rmtree(_temp_media, ignore_errors=True)
    settings.MEDIA_ROOT = settings._original_media_root
    del settings._original_media_root
    settings.DEFAULT_FILE_STORAGE = settings._original_file_storage
    del settings._original_file_storage
