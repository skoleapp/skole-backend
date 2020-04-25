from typing import Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _
from graphql import GraphQLError

from skole.models.comment import Comment
from skole.models.course import Course
from skole.models.resource import Resource
from skole.models.user import User
from skole.utils.constants import VoteConstants
from skole.utils.types import VotableModel


# Ignore: See explanation in UserManager.
class VoteManager(models.Manager):  # type: ignore[type-arg]
    def perform_vote(
        self, user: User, status: int, target: VotableModel
    ) -> Tuple[Optional["Vote"], int]:
        """Automatically create a new vote or delete one if it already exists."""

        if hasattr(target, "user") and target.user == user:
            raise GraphQLError(_("You can't vote for your own content."))

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

        if not vote:
            # We invert the status to revert the affect of the vote to the user's score.
            status = -status
        # Ignore: Mypy doesn't know that `target` always the `user` attribute.
        get_user_model().objects.change_score(target.user, status * multiplier)  # type: ignore[arg-type]

        return vote, target.score

    def check_existing_vote(
        self, user: User, status: int, **target: VotableModel
    ) -> Optional["Vote"]:
        try:
            vote = user.votes.get(**target)
            if vote.status == status:
                vote.delete()
                return None
            else:
                vote.status = status
                vote.save()
        except Vote.DoesNotExist:
            vote = self.model(**target)
            vote.user = user
            vote.status = status
            vote.save()
        return vote


class Vote(models.Model):
    """Models one vote on either comment, course or resource."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes"
    )
    status = models.IntegerField(choices=VoteConstants.STATUS)

    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, blank=True, related_name="votes"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=True, blank=True, related_name="votes"
    )
    resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, null=True, blank=True, related_name="votes"
    )

    objects = VoteManager()

    class Meta:
        unique_together = ("user", "comment", "course", "resource")

    def __str__(self) -> str:
        return f"{self.get_status_display()}, {self.user.username}"
