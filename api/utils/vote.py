from typing import Optional

import graphene
from graphql import ResolveInfo

from api.schemas.vote import VoteObjectType
from core.models import Comment, Course, Resource, Vote


class VoteMixin:
    points = graphene.Int()
    vote = graphene.Field(VoteObjectType)

    def resolve_vote(self, info: ResolveInfo) -> Optional[int]:
        """Resolve current user's vote if it exists."""

        user = info.context.user

        if user.is_anonymous:
            return None

        try:
            if isinstance(self, Comment):
                # Ignore: pk attribute will be defined in the class deriving from this mixin.
                return user.votes.get(comment=self.pk)  # type: ignore [attr-defined]
            if isinstance(self, Course):
                # Ignore: pk attribute will be defined in the class deriving from this mixin.
                return user.votes.get(course=self.pk)  # type: ignore [attr-defined]
            if isinstance(self, Resource):
                # Ignore: pk attribute will be defined in the class deriving from this mixin.
                return user.votes.get(resource=self.pk)  # type: ignore [attr-defined]
            else:
                raise TypeError("Invalid class.")

        except Vote.DoesNotExist:
            return None
