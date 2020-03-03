import datetime
import re

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from pytest import fixture

from core.models import Course, Resource, ResourceType


def test_str(db: fixture) -> None:
    resource1 = Resource.objects.get(pk=1)
    assert str(resource1) == "Sample exam 1"

    resource2 = Resource.objects.get(pk=2)
    assert str(resource2) == "Sample exam 2"


def test_create_resource(db: fixture, temp_media: fixture) -> None:
    resource_type = ResourceType.objects.get(pk=1)
    title = "title for resource"
    course = Course.objects.get(pk=1)
    file = SimpleUploadedFile("file1.txt", b"some data")
    user = get_user_model().objects.get(pk=2)
    date = datetime.date(2020, 1, 1)
    resource1 = Resource.objects.create_resource(
        resource_type=resource_type,
        title=title,
        course=course,
        file=file,  # type: ignore
        user=user,
        date=date,
    )
    assert resource1.resource_type == resource_type
    assert resource1.title == title
    assert resource1.course == course
    assert resource1.user == user
    assert resource1.date == date
    assert resource1.file == file
    assert re.match(
        r"^uploads/resources/file1\w*\.txt$", resource1.file.name,  # type: ignore
    )

    # Test that the date gets autopopulated if not passed explicitly.
    current_date = datetime.date.today()
    resource2 = Resource.objects.create_resource(
        resource_type=resource_type,
        title=title,
        course=course,
        files=files,  # type: ignore
        user=user,
    )
    assert resource2.date == current_date


def test_update_resource(db: fixture) -> None:
    resource = Resource.objects.get(pk=1)
    resource_type = ResourceType.objects.get(pk=2)
    title = "new title"
    date = datetime.date(2099, 1, 1)

    Resource.objects.update_resource(
        resource=resource, resource_type=resource_type, title=title, date=date
    )

    assert resource.resource_type == resource_type
    assert resource.title == title
    assert resource.date == date
