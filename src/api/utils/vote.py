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
    def mutate(cls, _, info: ResolveInfo, **kwargs) -> '_AbstractVoteMutation':
        if len(cls._meta.fields) != 1:
            raise AssertionError("Expected derived class to have exactly one graphene field.")

        target_object_type = list(cls._meta.fields.values())[0]._type
        target_model = target_object_type._meta.model

        id_field = f"{list(cls._meta.fields.keys())[0]}_id"
        target_id = kwargs.get(id_field, None)

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


