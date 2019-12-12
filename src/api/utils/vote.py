import abc
from typing import TypeVar

import graphene
from django.db import models
from graphql import ResolveInfo
from graphql_extensions.auth.decorators import login_required

from app.models import Vote
from app.utils.vote import DOWNVOTE, UPVOTE


class _VoteMeta(abc.ABCMeta, type(graphene.Mutation)):
    """When using multiple inheritance all base classes have to have the same metaclass.
    See: https://stackoverflow.com/q/28799089/9835872"""
    pass


class _AbstractVoteMutation(graphene.Mutation, abc.ABC, metaclass=_VoteMeta):
    T = TypeVar('T', bound='AbstractVoteMutation')

    @property
    @abc.abstractmethod
    def _vote_status(self) -> int:
        """Derived classes will set this value to upvote or downvote."""
        return NotImplemented

    @property
    @abc.abstractmethod
    def _target_model(self) -> models.Model:
        """Derived classes will set this value to the Model
        that is the target of the voting.
        """
        return NotImplemented

    @classmethod
    @login_required
    def mutate(cls, _, info: ResolveInfo, **kwargs) -> T:
        if len(kwargs) != 1 or not list(kwargs.keys())[0].endswith("_id"):
            raise AssertionError("This should take exactly one `foo_id` kwarg.")

        target_id = list(kwargs.values())[0]

        target = cls._target_model.objects.get(pk=target_id)
        try:
            vote = target.votes.get(creator=info.context.user)
            if vote.status == cls._vote_status:
                return cls(target)
            else:
                vote.delete()
        except Vote.DoesNotExist:
            pass

        Vote.objects.create_vote(
            creator=info.context.user,
            status=cls._vote_status,
            target=target,
        )
        return cls(target)


class AbstractUpvoteMutation(_AbstractVoteMutation):
    """Base class for all downvote mutations."""
    _vote_status = UPVOTE


class AbstractDownvoteMutation(_AbstractVoteMutation):
    """Base class for all upvote mutations."""
    _vote_status = DOWNVOTE


