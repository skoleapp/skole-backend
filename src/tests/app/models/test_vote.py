import pytest
from pytest import fixture

from app.models import Comment, Course, Resource, User, Vote


def test_str(db: fixture) -> None:
    vote1 = Vote.objects.get(pk=1)
    assert str(vote1) == "upvote, testuser2"

    vote2 = Vote.objects.get(pk=2)
    assert str(vote2) == "upvote, testuser3"


def test_manager_create_ok(db: fixture) -> None:
    user = User.objects.get(pk=2)
    status = 1

    targets = (
        Course.objects.get(pk=1),
        Resource.objects.get(pk=1),
        Comment.objects.get(pk=1),
    )

    for target in targets:
        vote = Vote.objects.create_vote(user=user, status=status, target=target)  # type: ignore[arg-type]
        assert vote.user == user
        assert vote.status == status

        # Check that only one foreign key reference is active.
        for attr in ("course", "resource", "comment"):
            if target.__class__.__name__.lower() == attr.replace("_", ""):
                assert getattr(vote, attr) == target
            else:
                assert getattr(vote, attr) is None


def test_manager_create_bad_target(db: fixture) -> None:
    user = User.objects.get(pk=2)
    bad_target = user
    with pytest.raises(TypeError):
        vote = Vote.objects.create_vote(user=user, status=1, target=bad_target)  # type: ignore[arg-type]


def test_manager_update_ok(db: fixture) -> None:
    comment = Comment.objects.get(pk=1)
    text = "new text"
    attachment = ""
    Comment.objects.update_comment(comment, text=text, attachment=attachment)
    assert comment.text == text
    assert comment.attachment == attachment
