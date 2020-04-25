from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from mypy.types import JsonDict

from skole.models import Starred, Vote
from skole.schemas.vote import VoteObjectType
from skole.utils.constants import Messages
from skole.utils.decorators import login_required_mutation
from skole.utils.forms import DeleteObjectForm


class DeleteMutationMixin:
    """A base class for all delete mutations."""

    message = graphene.String()

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
    @login_required_mutation
    def perform_mutate(
        cls, form: DeleteObjectForm, info: ResolveInfo
    ) -> "DeleteMutationMixin":
        obj = form.cleaned_data.get("target")
        obj.delete()
        # Ignore: Mypy doesn't know that this function will actually be used in a class
        #  deriving from DjangoModelFormMutation, where this type of calling cls with
        #  a graphene field name makes sense.
        return cls(message=Messages.OBJECT_DELETED)  # type: ignore[call-arg]


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


class StarredMixin:
    starred = graphene.Boolean()

    def resolve_starred(self, info: ResolveInfo) -> bool:
        """Check whether user has starred the current item."""

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
    """
    A mixin for passing the files of the request to the model form
    so that he validation can be done there.
    """

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        assert info.context is not None

        # Ignore: get_form_kwargs will exist in the super class when this mixin is used
        #   together with a DjangoModelFormMutation.
        form_kwargs = super().get_form_kwargs(root, info, **input)  # type: ignore[misc]
        form_kwargs["files"] = info.context.FILES
        if info.context.user:
            form_kwargs["instance"] = info.context.user
        return form_kwargs


class PaginationMixin:
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    count = graphene.Int()
