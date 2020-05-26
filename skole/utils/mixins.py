from typing import Any, Dict, Optional, Type, TypeVar

import graphene
from graphql import ResolveInfo
from mypy.types import JsonDict

from skole.models import Starred, Vote
from skole.utils.constants import MutationErrors
from skole.utils.forms import DeleteObjectForm

T = TypeVar("T", bound=graphene.Mutation)


class LoginRequiredMutationMixin:
    """Mixin for a mutation that needs a user to be logged in to use.

    Should be the first class in the inheritance list, at least before the graphql
    mutation class, e.g. DjangoModelFormMutation.
    """

    @classmethod
    def mutate(cls: Type[T], root: Any, info: ResolveInfo, input: JsonDict) -> T:
        assert info.context is not None

        if not info.context.user.is_authenticated:
            return cls(errors=MutationErrors.AUTH_REQUIRED)

        # Ignore: Mypy throws 'Unsupported argument 2 for "super"'.
        #   This works fine when the mixin is subclassed with a mutation class.
        return super().mutate(root, info, input)  # type: ignore[misc]


class VerificationRequiredMutationMixin:
    """Mixin for a mutation that needs a user to be verified (and logged in) to use.

    Should be the first class in the inheritance list, at least before the graphql
    mutation class, e.g. DjangoModelFormMutation.
    """

    @classmethod
    def mutate(cls: Type[T], root: Any, info: ResolveInfo, input: JsonDict) -> T:
        assert info.context is not None
        user = info.context.user

        if not user.is_authenticated:
            return cls(errors=MutationErrors.AUTH_REQUIRED)

        # By checking the authentication first, we avoid and error when AnonymousUser
        # doesn't have the verified attribute. This is also the reason why we cannot
        # make this a subclass of LoginRequiredMutationMixin, since then we would first
        # try to check verification here and face the same problem.

        if not user.verified:
            return cls(errors=MutationErrors.VERIFICATION_REQUIRED)

        # Ignore: Same as above.
        return super().mutate(root, info, input)  # type: ignore[misc]


class MessageMixin:
    """A mixin that provides a mutation a message field in the response."""

    message = graphene.String()


class DeleteMutationMixin(LoginRequiredMutationMixin, MessageMixin):
    """A base class for all delete mutations."""

    class Meta:
        return_field_name = "message"
        only_fields = ("id",)

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: Dict[str, Any]
    ) -> Dict[str, Any]:
        assert info.context is not None
        kwargs = {"data": input}
        pk = input.pop("id", None)

        if pk:
            # Ignore: Mypy can't see the _meta attribute.
            instance = cls._meta.model._default_manager.get(pk=pk)  # type: ignore[attr-defined]
            kwargs["instance"] = instance
            kwargs["user"] = info.context.user

        return kwargs

    @classmethod
    def perform_mutate(
        cls, form: DeleteObjectForm, info: ResolveInfo
    ) -> "DeleteMutationMixin":
        obj = form.cleaned_data.get("target")
        obj.delete()

        # Ignore 1: Mypy doesn't know that this function will actually be used in a class
        #   deriving from DjangoModelFormMutation, where this type of calling cls with
        #   a graphene field name makes sense.
        # Ignore 2: `get_success_message` will be defined in the baseclass.
        return cls(message=cls.get_success_message())  # type: ignore [call-arg, attr-defined]


class VoteMixin:
    """Adds a query for querying the vote status of the item for the current user."""

    score = graphene.Int()
    vote = graphene.Field("skole.schemas.vote.VoteObjectType")

    def resolve_vote(self, info: ResolveInfo) -> Optional[int]:
        """Return current user's vote if it exists."""

        assert info.context is not None
        user = info.context.user

        if user.is_anonymous:
            return None

        try:
            # Ignore: pk attribute will be defined in the class deriving from this mixin.
            return user.votes.get(**{self.__class__.__name__.lower(): self.pk})  # type: ignore [attr-defined]
        except Vote.DoesNotExist:
            return None


class StarredMixin:
    """Adds a query if the currently logged in user has starred the item."""

    starred = graphene.Boolean()

    def resolve_starred(self, info: ResolveInfo) -> bool:
        """Return True if the current user has starred the item, otherwise False."""

        assert info.context is not None
        user = info.context.user

        if user.is_anonymous:
            return False

        try:
            # Ignore: pk attribute will be defined in the class deriving from this mixin.
            return user.stars.get(**{self.__class__.__name__.lower(): self.pk}) is not None  # type: ignore [attr-defined]
        except Starred.DoesNotExist:
            return False


class FileMutationMixin:
    """A mixin for passing the files of the request to the model form so that he
    validation can be done there."""

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        assert info.context is not None

        # Ignore: get_form_kwargs will exist in the super class when this mixin is used
        #   together with a DjangoModelFormMutation.
        form_kwargs = super().get_form_kwargs(root, info, **input)  # type: ignore[misc]
        form_kwargs["files"] = info.context.FILES
        return form_kwargs


class PaginationMixin:
    """A mixin that provides a query all the fields required for pagination."""

    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    count = graphene.Int()
