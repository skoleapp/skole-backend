import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from skole.models import Comment, Course


@pytest.mark.django_db
def test_invalid_file_type() -> None:
    user = get_user_model().objects.get(pk=2)
    course = Course.objects.get(pk=1)
    invalid_file = SimpleUploadedFile("not_an_image.txt", b"file contents")

    with pytest.raises(ValidationError):
        Comment.objects.create(
            user=user, text="", attachment=invalid_file, course=course
        ).full_clean()


@pytest.mark.django_db
def test_invalid_file_extension() -> None:
    user = get_user_model().objects.get(pk=2)
    course = Course.objects.get(pk=1)
    actually_jpeg = SimpleUploadedFile("image.png", b"\xff\xd8\xff")

    with pytest.raises(ValidationError):
        Comment.objects.create(
            user=user, text="", attachment=actually_jpeg, course=course
        ).full_clean()


@pytest.mark.django_db
def test_too_large() -> None:
    user = get_user_model().objects.get(pk=2)
    course = Course.objects.get(pk=1)
    small_enough = SimpleUploadedFile("image.jpeg", b"\xff\xd8\xff" * 1_000_000)
    too_big = SimpleUploadedFile("image.jpeg", b"\xff\xd8\xff" * 2_000_000)

    Comment.objects.create(
        user=user, text="", attachment=small_enough, course=course
    ).full_clean()

    with pytest.raises(ValidationError):
        Comment.objects.create(
            user=user, text="", attachment=too_big, course=course
        ).full_clean()
