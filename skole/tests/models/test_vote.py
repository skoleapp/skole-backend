from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from skole.models import Comment, Thread, Vote
from skole.utils.constants import VoteConstants


@pytest.mark.django_db
def test_str() -> None:
    vote1 = Vote.objects.get(pk=1)
    assert str(vote1) == "upvote, testuser2"

    vote2 = Vote.objects.get(pk=2)
    assert str(vote2) == "upvote, testuser3"


@pytest.mark.django_db
def test_manager_perform_vote_ok() -> None:
    user = get_user_model().objects.get(pk=3)  # testuser3
    status = 1

    targets = (
        Thread.objects.get(pk=1),  # from testuser2
        Comment.objects.get(pk=18),  # from testuser9
    )

    for target in targets:
        vote, target_score = Vote.objects.perform_vote(user=user, status=status, target=target)  # type: ignore[arg-type]

        assert vote is not None
        assert vote.user == user
        assert vote.status == status

        if vote.thread is not None:
            thread = Thread.objects.get(pk=target.pk)
            assert target_score == thread.score == 1
            assert (
                thread.user
                and thread.user.score
                == target_score * VoteConstants.SCORE_THREAD_MULTIPLIER
            )
        elif vote.comment is not None:
            comment = Comment.objects.get(pk=target.pk)
            assert target_score == comment.score == 1
            assert (
                comment.user
                and comment.user.score
                == target_score * VoteConstants.SCORE_COMMENT_MULTIPLIER
            )

        # Check that only one foreign key reference is active.
        for attr in ("thread", "comment"):
            if target.__class__.__name__.lower() == attr:
                assert getattr(vote, attr) == target
            else:
                assert getattr(vote, attr) is None


@pytest.mark.django_db
def test_manager_perform_vote_existing() -> None:
    user = get_user_model().objects.get(pk=1)
    status = 1

    targets = (
        Thread.objects.get(pk=1),
        Comment.objects.get(pk=3),
    )

    for target in targets:
        vote, target_score = Vote.objects.perform_vote(user=user, status=status, target=target)  # type: ignore[arg-type]
        assert vote is not None
        assert target_score == 1

    for target in targets:
        vote, target_score = Vote.objects.perform_vote(user=user, status=status, target=target)  # type: ignore[arg-type]
        assert vote is None
        assert target_score == 0


@pytest.mark.django_db
def test_manager_perform_vote_bad_target() -> None:
    user = get_user_model().objects.get(pk=2)
    bad_target = user
    with pytest.raises(TypeError):
        # Ignore: `User` is obviously invalid and invalid type for the `target`
        #   argument, but that's exactly what we're testing here.
        Vote.objects.perform_vote(user=user, status=1, target=bad_target)  # type: ignore[arg-type]
