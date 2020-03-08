import pytest
from django.contrib.auth import get_user_model
from pytest import fixture

from core.models import Comment, Course, Resource, Vote


def test_str(db: fixture) -> None:
    vote1 = Vote.objects.get(pk=1)
    assert str(vote1) == "upvote, testuser2"

    vote2 = Vote.objects.get(pk=2)
    assert str(vote2) == "upvote, testuser3"


def test_manager_create_ok(db: fixture) -> None:
    user = get_user_model().objects.get(pk=1)
    status = 1

    targets = (
        Course.objects.get(pk=1),
        Resource.objects.get(pk=1),
        Comment.objects.get(pk=2),  # Does not have votes.
    )

    for target in targets:
        vote, target_points = Vote.objects.perform_vote(user=user, status=status, target=target)  # type: ignore[arg-type]

        assert vote is not None
        assert vote.user == user
        assert vote.status == status

        if vote.course is not None:
            course = Course.objects.get(pk=target.pk)
            assert target_points == course.points == 5  # type: ignore [attr-defined]
        elif vote.resource is not None:
            resource = Resource.objects.get(pk=target.pk)
            assert target_points == resource.points == 10  # type: ignore [attr-defined]
        elif vote.comment is not None:
            comment = Comment.objects.get(pk=target.pk)
            assert target_points == comment.points == 1  # type: ignore [attr-defined]

        # Check that only one foreign key reference is active.
        for attr in ("course", "resource", "comment"):
            if target.__class__.__name__.lower() == attr.replace("_", ""):
                assert getattr(vote, attr) == target
            else:
                assert getattr(vote, attr) is None


def test_manager_create_existing(db: fixture) -> None:
    user = get_user_model().objects.get(pk=1)
    status = 1

    targets = (
        Course.objects.get(pk=1),
        Resource.objects.get(pk=1),
        Comment.objects.get(pk=2),  # Does not have votes.
    )

    for target in targets:
        vote, target_points = Vote.objects.perform_vote(user=user, status=status, target=target)  # type: ignore[arg-type]
        assert vote is not None

        if vote.course is not None:
            course = Course.objects.get(pk=target.pk)
            assert target_points == course.points == 5  # type: ignore [attr-defined]
        elif vote.resource is not None:
            resource = Resource.objects.get(pk=target.pk)
            assert target_points == resource.points == 10  # type: ignore [attr-defined]
        elif vote.comment is not None:
            comment = Comment.objects.get(pk=target.pk)
            assert target_points == comment.points == 1  # type: ignore [attr-defined]

    for target in targets:
        vote, target_points = Vote.objects.perform_vote(user=user, status=status, target=target)  # type: ignore[arg-type]
        assert vote == None
        assert target_points == 0


def test_manager_create_bad_target(db: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    bad_target = user
    with pytest.raises(TypeError):
        vote, _ = Vote.objects.perform_vote(user=user, status=1, target=bad_target)  # type: ignore[arg-type]
