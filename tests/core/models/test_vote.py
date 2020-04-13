import pytest
from django.contrib.auth import get_user_model
from pytest import fixture

from core.models import Comment, Course, Resource, Vote
from core.utils.vote import (
    SCORE_COMMENT_MULTIPLIER,
    SCORE_COURSE_MULTIPLIER,
    SCORE_RESOURCE_MULTIPLIER,
)


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
        Resource.objects.get(pk=2),
        Comment.objects.get(pk=3),
    )

    for target in targets:
        vote, target_score = Vote.objects.perform_vote(user=user, status=status, target=target)  # type: ignore[arg-type]

        assert vote is not None
        assert vote.user == user
        assert vote.status == status

        if vote.course is not None:
            course = Course.objects.get(pk=target.pk)
            assert target_score == course.score == 1  # type: ignore [attr-defined]
            assert course.user.score == target_score * SCORE_COURSE_MULTIPLIER  # type: ignore [union-attr]
        elif vote.resource is not None:
            resource = Resource.objects.get(pk=target.pk)
            assert target_score == resource.score == 1  # type: ignore [attr-defined]
            assert resource.user.score == target_score * SCORE_RESOURCE_MULTIPLIER  # type: ignore [union-attr]
        elif vote.comment is not None:
            comment = Comment.objects.get(pk=target.pk)
            assert target_score == comment.score == 1  # type: ignore [attr-defined]
            assert comment.user.score == target_score * SCORE_COMMENT_MULTIPLIER  # type: ignore [union-attr]

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
        Resource.objects.get(pk=2),
        Comment.objects.get(pk=3),
    )

    for target in targets:
        vote, target_score = Vote.objects.perform_vote(user=user, status=status, target=target)  # type: ignore[arg-type]
        assert vote is not None

    for target in targets:
        vote, target_score = Vote.objects.perform_vote(user=user, status=status, target=target)  # type: ignore[arg-type]
        assert vote == None
        assert target_score == 0


def test_manager_create_bad_target(db: fixture) -> None:
    user = get_user_model().objects.get(pk=2)
    bad_target = user
    with pytest.raises(TypeError):
        vote, _ = Vote.objects.perform_vote(user=user, status=1, target=bad_target)  # type: ignore[arg-type]
