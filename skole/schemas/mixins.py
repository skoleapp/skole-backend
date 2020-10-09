from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Type, TypeVar

import graphene
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_django.types import ErrorType
from graphql import ResolveInfo

from skole.models import SkoleModel, Starred, Vote
from skole.types import JsonDict
from skole.utils.constants import MutationErrors
from skole.utils.shortcuts import validate_is_first_inherited

if TYPE_CHECKING:  # pragma: no cover
    # To avoid circular import.
    from skole.forms.base import SkoleUpdateModelForm


T = TypeVar("T", bound="SkoleCreateUpdateMutationMixin")


class SuccessMessageMixin:
    """
    A mixin that provides a mutation a message field in the response.

    Attributes:
        success_message: This has to be set to the string that the mutation
            should return in a successful response.
    """

    success_message: str

    message = graphene.String()

    @classmethod
    def perform_mutate(
        cls,
        form: Any,
        info: ResolveInfo
        # Keep the type as Any to silence warnings about breaking Liskov
        # substitution principle.
        # https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
    ) -> DjangoModelFormMutation:
        # Ignore: Will be defined in subclasses.
        obj = super().perform_mutate(form, info)  # type: ignore[misc]
        obj.message = cls.success_message
        return obj


class VoteMixin:
    """Adds a query for querying the vote status of the item for the current user."""

    score = graphene.Int()
    vote = graphene.Field("skole.schemas.vote.VoteObjectType")

    @staticmethod
    def resolve_vote(root: SkoleModel, info: ResolveInfo) -> Optional[Vote]:
        """Return current user's vote if it exists."""

        assert info.context is not None
        user = info.context.user

        if user.is_anonymous:
            return None

        try:
            return user.votes.get(**{root.__class__.__name__.lower(): root.pk})
        except Vote.DoesNotExist:
            return None


class StarredMixin:
    """Adds a query if the currently logged in user has starred the item."""

    starred = graphene.Boolean()

    @staticmethod
    def resolve_starred(root: SkoleModel, info: ResolveInfo) -> bool:
        """Return True if the current user has starred the item, otherwise False."""

        assert info.context is not None
        user = info.context.user

        if user.is_anonymous:
            return False

        try:
            return (
                user.stars.get(**{root.__class__.__name__.lower(): root.pk}) is not None
            )
        except Starred.DoesNotExist:
            return False


class PaginationMixin:
    """A mixin that provides a query all the fields required for pagination."""

    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    count = graphene.Int()


@validate_is_first_inherited
class SkoleCreateUpdateMutationMixin:
    """
    Base mixin for all create and update mutations.

    This cannot be a base class, because all graphene mutation classes require
    their subclasses to define a `form_class` in their `Meta`,
    and it doesn't make sense to define here.

    Attributes:
        login_required: Whether the mutation can only be used by logged in users.
        verification_required: Whether the mutation can only be used by verified users.
            This also automatically implies that the user has to be logged in.
    """

    login_required: bool = False
    verification_required: bool = False

    # Defined here to add the default value.
    errors = graphene.List(ErrorType, default_value=[])

    @classmethod
    def get_form_kwargs(
        cls, root: None, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        # Ignore: Will be defined in subclasses.
        kwargs = super().get_form_kwargs(root, info, **input)  # type: ignore[misc]
        kwargs["request"] = info.context
        return kwargs

    @classmethod
    def mutate(cls: Type[T], root: None, info: ResolveInfo, **input: JsonDict) -> T:
        assert info.context is not None
        user = info.context.user

        if cls.login_required or cls.verification_required:
            if not user.is_authenticated:
                # Ignore: `errors` is valid arg in subclasses.
                return cls(errors=MutationErrors.AUTH_REQUIRED)  # type: ignore[call-arg]

        if cls.verification_required:
            if not user.verified:
                # Ignore: `errors` is valid arg in subclasses.
                return cls(errors=MutationErrors.VERIFICATION_REQUIRED)  # type: ignore[call-arg]

        # Ignore: Will be defined in subclasses.
        return super().mutate(root, info, **input)  # type: ignore[misc]


@validate_is_first_inherited
class SkoleDeleteMutationMixin(SkoleCreateUpdateMutationMixin, SuccessMessageMixin):
    """
    Base mixin for all object deletion mutations.

    When subclassing from this it most likely makes sense to also subclass the Meta:
        class Meta(SkoleDeleteMutationMixin.Meta):
            form_class = FooForm

    Attributes:
        success_message: This has to be set to the string that the mutation
            should return in a successful response.
    """

    login_required = True

    class Meta:
        return_field_name = "message"
        only_fields = ("id",)

    @classmethod
    def perform_mutate(
        cls, form: SkoleUpdateModelForm, info: ResolveInfo
    ) -> SkoleCreateUpdateMutationMixin:
        form.instance.soft_delete()
        return super().perform_mutate(form, info)
