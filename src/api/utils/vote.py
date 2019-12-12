import graphene
from django.db import models
from graphql import ResolveInfo
from graphql_extensions.auth.decorators import login_required

from app.models import Vote
from app.utils.vote import DOWNVOTE, UPVOTE


class _AbstractVoteMutation(graphene.Mutation):
    """Base class for both of the abstract vote mutations,
    this should not be subclassed elsewhere.
    """
    _target_type: models.Model
    _vote_status: int

    @classmethod
    @login_required
    def mutate(cls, _, info: ResolveInfo, **kwargs) -> '_AbstractVoteMutation':
        if len(kwargs) != 1 or not list(kwargs.keys())[0].endswith("_id"):
            raise AssertionError("This should take exactly one `foo_id` kwarg.")

        target_id = list(kwargs.values())[0]

        target = cls._target_type._meta.model.objects.get(pk=target_id)
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
    """Base class for all downvote mutations.
    Users of this class still have to remember to override the value of _target_type.
    """
    _vote_status = UPVOTE


class AbstractDownvoteMutation(_AbstractVoteMutation):
    """Base class for all upvote mutations.
    Users of this class still have to remember to override the value of _target_type.
    """
    _vote_status = DOWNVOTE


