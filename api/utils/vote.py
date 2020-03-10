from typing import Optional

import graphene
from graphql import ResolveInfo

from api.schemas.vote import VoteObjectType
from core.models import Vote


class VoteMixin:
    points = graphene.Int()
    vote = graphene.Field(VoteObjectType)

    def resolve_vote(self, info: ResolveInfo) -> Optional[int]:
        """Resolve current user's vote if it exists."""

        user = info.context.user

        if user.is_anonymous:
            return None

        try:
            return user.votes.get(comment=self.pk)  # type: ignore [attr-defined]
        except Vote.DoesNotExist:
            return None
