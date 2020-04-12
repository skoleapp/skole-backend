from typing import Optional, Tuple

from django.db import models
from django.utils.translation import gettext as _
from graphql import GraphQLError

from core.models.comment import Comment
from core.models.course import Course
from core.models.resource import Resource
from core.models.user import User
from core.utils.types import VotableModel
from core.utils.vote import VOTE_STATUS


class VoteManager(models.Manager["Vote"]):
    def perform_vote(
        self, user: User, status: int, target: VotableModel
    ) -> Tuple[Optional["Vote"], int]:
        """Automatically create a new vote or delete one if it already exists."""

        if hasattr(target, "user") and target.user == user:
            raise GraphQLError(_("You can't vote for your own content."))

        if isinstance(target, Comment):
            vote = self.check_existing_vote(user, status, comment=target)
        elif isinstance(target, Course):
            vote = self.check_existing_vote(user, status, course=target)
        elif isinstance(target, Resource):
            vote = self.check_existing_vote(user, status, resource=target)
        else:
            raise TypeError(f"Invalid target type for Vote: {type(target)}")

        return vote, target.points

    def check_existing_vote(
        self, user: User, status: int, **target: VotableModel
    ) -> Optional["Vote"]:
        try:
            vote = user.votes.get(**target)

            if vote.status == status:
                vote.delete()
                return None

            vote.status = status
            vote.save()
            return vote

        except Vote.DoesNotExist:
            vote = self.model(**target)
            vote.user = user
            vote.status = status
            vote.save()
            return vote


class Vote(models.Model):
    """Models one vote on either comment, course or resource."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    status = models.IntegerField(choices=VOTE_STATUS)

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
        unique_together = ("comment", "course", "resource", "user")

    def __str__(self) -> str:
        return f"{self.get_status_display()}, {self.user.username}"
