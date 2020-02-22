from typing import Optional, Tuple, Union

from django.db import models

from core.models.comment import Comment
from core.models.course import Course
from core.models.resource import Resource
from core.models.user import User
from core.utils.vote import VOTE_STATUS


class VoteManager(models.Manager):  # type: ignore[type-arg]
    def perform_vote(
        self, user: User, status: int, target: Union[Comment, Course, Resource]
    ) -> Tuple[Optional["Vote"], int]:
        """Automatically create a new vote or delete one if it already exists."""

        if isinstance(target, Comment):
            vote = self.check_existing_vote(user, status, comment=target)
            # target_points = Comment.objects.get(pk=target.pk).points # type: ignore [attr-defined]
        elif isinstance(target, Course):
            vote = self.check_existing_vote(user, status, course=target)
            # target_points = Course.objects.get(pk=target.pk).points # type: ignore [attr-defined]
        elif isinstance(target, Resource):
            vote = self.check_existing_vote(user, status, resource=target)
            # target_points = Resource.objects.get(pk=target.pk).points # type: ignore [attr-defined]
        else:
            raise TypeError(f"Invalid target type for Vote: {type(target)}")

        return vote, target.points  # type: ignore [union-attr]

    def check_existing_vote(
        self, user: User, status: int, **target: Union[Comment, Course, Resource]
    ) -> Optional["Vote"]:
        try:
            vote = user.votes.get(**target)  # type: ignore [attr-defined]

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
        return f"{self.get_status_display()}, {self.user.username}"  # type: ignore[attr-defined]
