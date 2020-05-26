import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from pytest import fixture

from skole.models import Comment, Course


def test_invalid_file_type(db: fixture, temp_media: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    target = Course.objects.get(pk=1)
    invalid_file = SimpleUploadedFile("not_an_image.txt", b"file contents")

    with pytest.raises(ValidationError):
        Comment.objects.create_comment(
            user=user, text="", attachment=invalid_file, target=target,
        ).full_clean()


def test_invalid_file_extension(db: fixture, temp_media: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    target = Course.objects.get(pk=1)
    actually_jpeg = SimpleUploadedFile("image.png", b"\xff\xd8\xff")

    with pytest.raises(ValidationError):
        Comment.objects.create_comment(
            user=user, text="", attachment=actually_jpeg, target=target,
        ).full_clean()


def test_too_large(db: fixture, temp_media: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    target = Course.objects.get(pk=1)
    small_enough = SimpleUploadedFile("image.jpeg", b"\xff\xd8\xff" * 1_000_000)
    too_big = SimpleUploadedFile("image.jpeg", b"\xff\xd8\xff" * 2_000_000)

    Comment.objects.create_comment(
        user=user, text="", attachment=small_enough, target=target,
    ).full_clean()

    with pytest.raises(ValidationError):
        Comment.objects.create_comment(
            user=user, text="", attachment=too_big, target=target,
        ).full_clean()
