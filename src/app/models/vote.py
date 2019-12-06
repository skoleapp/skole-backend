from django.db import models

from app.utils.vote import VOTE_STATUS
from .comment import Comment
from .course import Course
from .resource import Resource
from .user import User


class Vote(models.Model):
    # TODO: add manager, which enforces that only one of the foreignkeyrefs are in use at a time.
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, related_name="votes")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, related_name="votes")
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, related_name="votes")

    status = models.IntegerField(choices=VOTE_STATUS)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")

    class Meta:
        unique_together = ("comment", "course", "resource", "creator")
