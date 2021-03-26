from __future__ import annotations

from typing import Any, ClassVar, Optional

import graphene
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.models import SkoleModel, Vote
from skole.types import ResolveInfo


class SuccessMessageMixin:
    """
    A mixin that provides a mutation a success message field in the response.

    Attributes:
        success_message_value: This has to be set to the string that the mutation
            should return in a successful response.
    """

    success_message_value: ClassVar[str]

    success_message = graphene.String()

    @classmethod
    def perform_mutate(
        cls,
        # Keep the type as Any to silence warnings about breaking Liskov
        # substitution principle.
        # https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        form: Any,
        info: ResolveInfo,
    ) -> DjangoModelFormMutation:
        # Ignore: Will be defined in subclasses.
        obj = super().perform_mutate(form, info)  # type: ignore[misc]
        obj.success_message = cls.success_message_value
        return obj


class VoteMixin:
    """Adds a query for querying the vote status of the item for the current user."""

    score = graphene.Int()
    vote = graphene.Field("skole.schemas.vote.VoteObjectType")

    @staticmethod
    def resolve_vote(root: SkoleModel, info: ResolveInfo) -> Optional[Vote]:
        """Return current user's vote if it exists."""
        user = info.context.user

        if user.is_anonymous:
            return None

        # Ignore: Mypy incorrectly thinks that `RelatedManager[Vote]` doesn't have this method.
        return user.votes.get_or_none(**{root.__class__.__name__.lower(): root.pk})  # type: ignore[attr-defined]


class StarMixin:
    """Adds a query if the currently logged in user has starred the item."""

    starred = graphene.Boolean()

    @staticmethod
    def resolve_starred(root: SkoleModel, info: ResolveInfo) -> bool:
        """Return True if the current user has starred the item, otherwise False."""

        user = info.context.user

        if user.is_anonymous:
            return False

        return user.stars.filter(**{root.__class__.__name__.lower(): root.pk}).exists()


class PaginationMixin:
    """A mixin that provides a query all the fields required for pagination."""

    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    count = graphene.Int()
