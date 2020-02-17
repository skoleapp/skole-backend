from typing import Union

from django.db import models

from app.utils.vote import VOTE_STATUS

from .comment import Comment
from .course import Course
from .resource import Resource
from .user import User


class VoteManager(models.Manager):  # type: ignore[type-arg]
    def perform_vote(
        self, user: User, status: int, target: Union[Comment, Course, Resource]
    ) -> "Vote":
        """Automatically create a new vote or delete one if it already exists."""

        if isinstance(target, Comment):
            return self.check_existing_vote(user, status, comment=target)
        elif isinstance(target, Course):
            return self.check_existing_vote(user, status, course=target)
        elif isinstance(target, Resource):
            return self.check_existing_vote(user, status, resource=target)
        else:
            raise TypeError(f"Invalid target type for Vote: {type(target)}")

    def check_existing_vote(
        self, user: User, status: int, **target: Union[Comment, Course, Resource]
    ) -> "Vote":
        try:
            vote = user.votes.get(**target)  # type: ignore [attr-defined]

            if vote.status == status:
                vote.delete()
                return None  # type: ignore [return-value]

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
        return f"{self.get_status_display()}, {self.user.username}"  # type: ignore[attr-defined]
