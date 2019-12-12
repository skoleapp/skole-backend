from typing import Union

from django.db import models

from app.utils.vote import VOTE_STATUS
from .comment import Comment
from .course import Course
from .resource import Resource
from .user import User


class VoteManager(models.Manager):
    def create_vote(self, creator: User, status: int,
                    target: Union[Comment, Course, Resource]) -> 'Vote':
        if isinstance(target, Comment):
            vote = self.model(comment=target)
        elif isinstance(target, Course):
            vote = self.model(course=target)
        elif isinstance(target, Resource):
            vote = self.model(resource=target)
        else:
            raise TypeError(f"Invalid target type for Vote: {type(target)}")

        vote.creator = creator
        vote.status = status

        vote.save()
        return vote


class Vote(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, related_name="votes")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, related_name="votes")
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, related_name="votes")

    status = models.IntegerField(choices=VOTE_STATUS)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")

    objects = VoteManager()

    class Meta:
        unique_together = ("comment", "course", "resource", "creator")