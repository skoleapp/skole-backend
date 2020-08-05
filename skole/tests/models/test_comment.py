import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from skole.models import Comment, Course, Resource
from skole.tests.helpers import is_slug_match
from skole.utils.types import Fixture


def test_str(db: Fixture) -> None:
    comment1 = Comment.objects.get(pk=1)
    assert str(comment1) == "Starting comment for the thread on a res..."

    comment2 = Comment.objects.get(pk=2)
    assert str(comment2) == "Second comment of the thread."

    comment3 = Comment.objects.get(pk=3)
    assert str(comment3) == "Attachment Comment: 3"


def test_manager_create_ok(db: Fixture, temp_media: Fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    text = "A comment."

    targets = (
        Course.objects.get(pk=1),
        Resource.objects.get(pk=1),
        Comment.objects.get(pk=1),
    )

    for target in targets:
        # Somehow the file needs to be created on each iteration of the loop, otherwise
        # the file type will be application/x-empty on the second iterations.
        # Source for the jpeg bit pattern: https://en.wikipedia.org/wiki/List_of_file_signatures
        attachment = SimpleUploadedFile("image.jpeg", b"\xff\xd8\xff")
        comment = Comment.objects.create_comment(
            user=user, text=text, attachment=attachment, target=target
        )

        assert comment.user == user
        assert comment.text == text

        # Filenames after the first created comment will have a random glob to make them unique.
        assert is_slug_match(
            "media/uploads/attachments/image.jpeg", comment.attachment.url
        )

        # Check that only one foreign key reference is active.
        for attr in ("course", "resource", "comment"):
            if target.__class__.__name__.lower() == attr.replace("_", ""):
                assert getattr(comment, attr) == target
            else:
                assert getattr(comment, attr) is None


def test_manager_create_bad_target(db: Fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    bad_target = user
    with pytest.raises(TypeError):
        Comment.objects.create_comment(
            user=user, text="foo", attachment=None, target=bad_target
        )


def test_manager_update_ok(db: Fixture) -> None:
    comment = Comment.objects.get(pk=1)
    text = "new text"
    attachment = ""
    Comment.objects.update_comment(comment, text=text, attachment=attachment)
    assert comment.text == text
    assert comment.attachment == attachment
