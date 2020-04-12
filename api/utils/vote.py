from typing import Optional

import graphene
from graphql import ResolveInfo

from api.schemas.vote import VoteObjectType
from core.models import Vote


class VoteMixin:
    score = graphene.Int()
    vote = graphene.Field(VoteObjectType)

    def resolve_vote(self, info: ResolveInfo) -> Optional[int]:
        """Resolve current user's vote if it exists."""
        assert info.context is not None

        user = info.context.user

        if user.is_anonymous:
            return None

        try:
            # Ignore: pk attribute will be defined in the class deriving from this mixin.
            return user.votes.get(**{self.__class__.__name__.lower(): self.pk})  # type: ignore [attr-defined]
        except Vote.DoesNotExist:
            return None
