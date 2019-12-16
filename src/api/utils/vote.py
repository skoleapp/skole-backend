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
    _vote_status: int

    @classmethod
    @login_required
    def mutate(cls, _, info: ResolveInfo, **kwargs: int) -> '_AbstractVoteMutation':
        if len(cls._meta.fields) != 1 or len(cls._meta.arguments) != 1 or len(kwargs) != 1:
            raise AssertionError(
                "Expected derived mutation to have exactly one graphene field and taking exactly one argument.")

        # Get the model we are mutating, e.g. Course
        target_model = next(iter(cls._meta.fields.values()))._type._meta.model

        # Get the value of the passed kwarg, e.g. the value of `course_id`
        _, target_id = kwargs.popitem()

        target = target_model.objects.get(pk=target_id)
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


