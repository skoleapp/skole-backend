import re

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from pytest import fixture

from core.models import Comment, Course, Resource


def test_str(db: fixture) -> None:
    comment1 = Comment.objects.get(pk=1)
    assert str(comment1) == "Starting comment for the thread on a res..."

    comment2 = Comment.objects.get(pk=2)
    assert str(comment2) == "Second comment of the thread."


def test_manager_create_ok(db: fixture, temp_media: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    text = "A comment."
    attachment = SimpleUploadedFile("test_notes.txt", b"file contents")

    targets = (
        Course.objects.get(pk=1),
        Resource.objects.get(pk=1),
        Comment.objects.get(pk=1),
    )

    for target in targets:
        comment = Comment.objects.create_comment(
            user=user, text=text, attachment=attachment, target=target  # type: ignore[arg-type]
        )

        assert comment.user == user
        assert comment.text == text

        # Filenames after the first created comment will have a random glob to make them unique.
        assert re.match(
            r"^uploads/attachments/test_notes\w*\.txt$", comment.attachment.name
        )

        # Check that only one foreign key reference is active.
        for attr in ("course", "resource", "comment"):
            if target.__class__.__name__.lower() == attr.replace("_", ""):
                assert getattr(comment, attr) == target
            else:
                assert getattr(comment, attr) is None


def test_manager_create_bad_target(db: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    bad_target = user
    with pytest.raises(TypeError):
        comment = Comment.objects.create_comment(
            user=user, text="foo", attachment=None, target=bad_target
        )


def test_manager_update_ok(db: fixture) -> None:
    comment = Comment.objects.get(pk=1)
    text = "new text"
    attachment = ""
    Comment.objects.update_comment(comment, text=text, attachment=attachment)
    assert comment.text == text
    assert comment.attachment == attachment
