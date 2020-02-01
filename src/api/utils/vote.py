from typing import Any

import graphene
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from api.utils.common import get_object_from_meta_and_kwargs
from app.models import Vote
from app.utils.vote import DOWNVOTE, UPVOTE


class _AbstractVoteMutation(graphene.Mutation):
    """Base class for both of the abstract vote mutations,
    this should not be subclassed elsewhere.
    """

    _vote_status: int

    @classmethod
    @login_required
    def mutate(
        cls, root: Any, info: ResolveInfo, **kwargs: int
    ) -> "_AbstractVoteMutation":
        target = get_object_from_meta_and_kwargs(cls._meta, kwargs)

        try:
            vote = target.votes.get(user=info.context.user)
            if vote.status == cls._vote_status:
                return cls(target)
            else:
                vote.delete()
        except Vote.DoesNotExist:
            pass

        Vote.objects.create_vote(
            user=info.context.user, status=cls._vote_status, target=target,
        )
        return cls(target)


class AbstractUpvoteMutation(_AbstractVoteMutation):
    """Base class for all downvote mutations.
    This can be subclassed in any schema that needs a upvote mutation.
    """

    _vote_status = UPVOTE


class AbstractDownvoteMutation(_AbstractVoteMutation):
    """Base class for all upvote mutations.
    This can be subclassed in any schema that needs a downvote mutation.
    """

    _vote_status = DOWNVOTE
