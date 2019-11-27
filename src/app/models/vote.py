from django.db import models

from app.utils.vote import VOTE_STATUS
from .user import User
from .vote_holder import VoteHolder


class Vote(models.Model):
    vote_holder = models.ForeignKey(VoteHolder, on_delete=models.CASCADE, related_name="votes")
    status = models.IntegerField(choices=VOTE_STATUS)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")

    class Meta:
        unique_together = ("vote_holder", "creator")
