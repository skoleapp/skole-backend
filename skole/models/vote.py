from __future__ import annotations

from typing import Literal, Optional

from django.conf import settings
from django.db import models

from skole.models.base import SkoleManager, SkoleModel
from skole.models.comment import Comment
from skole.models.thread import Thread
from skole.models.user import User
from skole.types import VotableModel
from skole.utils.constants import VoteConstants
from skole.utils.shortcuts import full_refresh_from_db


class VoteManager(SkoleManager["Vote"]):
    def perform_vote(
        self, user: User, status: Literal[1, -1], target: VotableModel
    ) -> tuple[Optional[Vote], int]:
        """Create a new vote to the target or delete it if it already exists."""

        if isinstance(target, Comment):
            multiplier = VoteConstants.SCORE_COMMENT_MULTIPLIER
            vote = self.check_existing_vote(user, status, comment=target)
        elif isinstance(target, Thread):
            multiplier = VoteConstants.SCORE_THREAD_MULTIPLIER
            vote = self.check_existing_vote(user, status, thread=target)
        else:
            raise TypeError(f"Invalid target type for Vote: {type(target)}")

        if target.user:
            target.user.change_score(
                # Invert the status to revert the affect to the user's score.
                (status if vote else -status)
                * multiplier
            )

        # Have to query the object again since `score` is an annotation.
        target = full_refresh_from_db(target)

        return vote, target.score

    def check_existing_vote(
        self, user: User, status: int, **target: VotableModel
    ) -> Optional[Vote]:
        try:
            vote = user.votes.get(**target)
            if vote.status == status:
                vote.delete()
                # Already had an upvote, and re-upvoted it -> clear the vote.
                return None
            else:
                # Had a previous downvote, and are now upvoting it -> change the status.
                vote.status = status
                vote.save()
        except Vote.DoesNotExist:
            # No previous vote -> create one.
            vote = self.model(**target)
            vote.user = user
            vote.status = status
            vote.save()
        return vote


class Vote(SkoleModel):
    """Models one vote on either a comment or a thread."""

    _identifier_field = "user"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="votes",
    )

    status = models.IntegerField(choices=VoteConstants.STATUS)

    comment = models.ForeignKey(
        "skole.Comment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="votes",
    )

    thread = models.ForeignKey(
        "skole.Thread",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="votes",
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = VoteManager()

    class Meta:
        unique_together = ("user", "comment", "thread")

    def __str__(self) -> str:
        if self.user is not None:
            return f"{self.get_status_display()}, {self.user.username}"
        else:
            return f"{self.get_status_display()}, deleted user"
