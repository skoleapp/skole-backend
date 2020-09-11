from typing import Literal, Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from skole.types import VotableModel
from skole.utils.constants import VoteConstants
from skole.utils.shortcuts import full_refresh_from_db

from .base import SkoleManager, SkoleModel
from .comment import Comment
from .course import Course
from .resource import Resource
from .user import User


class VoteManager(SkoleManager):
    def perform_vote(
        self, user: User, status: Literal[1, -1], target: VotableModel
    ) -> Tuple[Optional["Vote"], int]:
        """Create a new vote to the target or delete it if it already exists."""

        if isinstance(target, Comment):
            multiplier = VoteConstants.SCORE_COMMENT_MULTIPLIER
            vote = self.check_existing_vote(user, status, comment=target)
        elif isinstance(target, Course):
            multiplier = VoteConstants.SCORE_COURSE_MULTIPLIER
            vote = self.check_existing_vote(user, status, course=target)
        elif isinstance(target, Resource):
            multiplier = VoteConstants.SCORE_RESOURCE_MULTIPLIER
            vote = self.check_existing_vote(user, status, resource=target)
        else:
            raise TypeError(f"Invalid target type for Vote: {type(target)}")

        if target.user:
            get_user_model().objects.change_score(
                target.user,
                # Invert the status to revert the affect to the user's score.
                (status if vote else -status) * multiplier,
            )

        # Have to query the object again since `score` is an annotation.
        target = full_refresh_from_db(target)

        return vote, target.score

    def check_existing_vote(
        self, user: User, status: int, **target: VotableModel
    ) -> Optional["Vote"]:
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
    """Models one vote on either comment, course or resource."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes"
    )

    status = models.IntegerField(choices=VoteConstants.STATUS)

    comment = models.ForeignKey(
        "skole.Comment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="votes",
    )

    course = models.ForeignKey(
        "skole.Course",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="votes",
    )

    resource = models.ForeignKey(
        "skole.Resource",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="votes",
    )

    # Ignore: Mypy somehow thinks that this is incompatible with the super class.
    objects = VoteManager()  # type: ignore[assignment]

    class Meta:
        unique_together = ("user", "comment", "course", "resource")

    def __str__(self) -> str:
        return f"{self.get_status_display()}, {self.user.username}"
