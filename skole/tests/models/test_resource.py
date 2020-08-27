import datetime

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from skole.models import Course, Resource, ResourceType
from skole.tests.helpers import is_slug_match
from skole.utils.types import Fixture


def test_str(db: Fixture) -> None:
    resource1 = Resource.objects.get(pk=1)
    assert str(resource1) == "Sample exam 1"

    resource2 = Resource.objects.get(pk=2)
    assert str(resource2) == "Sample exam 2"


def test_create_and_update_resource(db: Fixture) -> None:
    resource_type = ResourceType.objects.get(pk=1)
    title = "title for resource"
    course = Course.objects.get(pk=1)
    # Source for the pdf bit pattern: https://en.wikipedia.org/wiki/List_of_file_signatures
    file = SimpleUploadedFile("exam.pdf", b"\x25\x50\x44\x46\x2d")
    user = get_user_model().objects.get(pk=2)
    date = datetime.date(2020, 1, 1)
    resource1 = Resource.objects.create_resource(
        resource_type=resource_type,
        title=title,
        course=course,
        file=file,
        user=user,
        date=date,
    )
    assert resource1.resource_type == resource_type
    assert resource1.title == title
    assert resource1.course == course
    assert resource1.user == user
    assert resource1.date == date
    assert is_slug_match("/media/uploads/resources/exam.pdf", resource1.file.url)

    # Somehow the file needs to be created for validation to work.
    file = SimpleUploadedFile("exam.pdf", b"\x25\x50\x44\x46\x2d")

    # Test that the date gets autopopulated if not passed explicitly.
    current_date = datetime.date.today()
    resource2 = Resource.objects.create_resource(
        resource_type=resource_type, title=title, course=course, file=file, user=user,
    )
    assert resource2.date == current_date

    # Test that updating the newly created resource works fine.
    new_resource_type = ResourceType.objects.get(pk=4)
    new_title = "new title"
    new_date = datetime.date(2099, 1, 1)

    Resource.objects.update_resource(
        resource=resource2,
        resource_type=new_resource_type,
        title=new_title,
        date=new_date,
    )

    assert resource2.resource_type == new_resource_type
    assert resource2.title == new_title
    assert resource2.date == new_date
