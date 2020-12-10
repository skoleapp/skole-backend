from __future__ import annotations

import inspect
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Tuple,
    Type,
    TypeVar,
    cast,
    get_type_hints,
)

import graphene.utils.orderedtype
import graphene_django
from graphene.types.unmountedtype import UnmountedType
from graphene.utils.subclass_with_meta import SubclassWithMeta_Meta
from graphene_django.types import ErrorType

from skole.forms.base import SkoleUpdateModelForm
from skole.models import User
from skole.schemas.mixins import PaginationMixin, SuccessMessageMixin
from skole.types import JsonDict, ResolveInfo
from skole.utils import api_descriptions
from skole.utils.constants import MutationErrors
from skole.utils.shortcuts import validate_is_first_inherited

T = TypeVar("T", bound="SkoleObjectTypeMeta")
M = TypeVar("M", bound="SkoleCreateUpdateMutationMixin")


class SkoleObjectTypeMeta(SubclassWithMeta_Meta):
    """
    Metaclass which makes docstrings and other code properties into GraphQL API docs.

    This takes resolver docstrings into the graphene fields description attribute.

    This also adds commonly needed info that can normally only be seen from the code,
    such as whether the query or mutation requires authentication to work, to the docs.
    """

    def __new__(  # pylint: disable=arguments-differ; (parent's signature is unidiomatic)
        mcs: Type[T], name: str, bases: Tuple[type, ...], attrs: Dict[str, Any]
    ) -> T:
        cls = cast(T, super().__new__(mcs, name, bases, attrs))

        if not isinstance(cls, graphene_django.DjangoObjectType):
            # No need to dynamically generate descriptions for Django object type resolvers.

            for attr in attrs:
                if attr.startswith("resolve_") and (
                    field := getattr(cls, attr.removeprefix("resolve_"), None)
                ):
                    resolver = getattr(cls, attr)
                    # This needs to be done after `cls` is created because
                    # `@staticmethod`s haven't been resolved in just `attrs`.
                    if description := mcs._build_resolver_description(resolver, field):
                        if isinstance(field, UnmountedType):
                            # The two field types take the description differently.
                            field.kwargs["description"] = description
                        else:  # `MountedType`
                            field.description = description

        if cls._meta and (description := mcs._build_cls_description(cls)):
            # We need to bypass `graphene.types.BaseOptions` "frozen" check.
            object.__setattr__(cls._meta, "description", description)

        return cls

    @staticmethod
    def _build_cls_description(  # pylint: disable=bad-staticmethod-argument
        cls: T,
    ) -> str:
        description = []

        if issubclass(cls, graphene_django.DjangoObjectType):
            if model_doc := cls._meta.model.__doc__:
                description.append(inspect.cleandoc(model_doc))

        if original_description := getattr(cls._meta, "description", None):
            description.append(original_description)

        if cls.__doc__:
            if (cleaned_doc := inspect.cleandoc(cls.__doc__)) != original_description:
                description.append(cleaned_doc)

        form_class = getattr(cls._meta, "form_class", None)
        if form_class and issubclass(form_class, SkoleUpdateModelForm):
            description.append(api_descriptions.OWNERSHIP_REQUIRED)

        if getattr(cls, "verification_required", False):
            description.append(api_descriptions.VERIFICATION_REQUIRED)
        elif getattr(cls, "login_required", False):
            description.append(api_descriptions.AUTH_REQUIRED)

        if issubclass(cls, PaginationMixin):
            description.append(api_descriptions.PAGINATED)

        return "\n\n".join(description)

    @staticmethod
    def _build_resolver_description(
        resolver: Callable[..., Any], field: graphene.utils.orderedtype.OrderedType
    ) -> str:
        description = []

        if original_description := getattr(field, "description", None):
            # `field` was of `MountedType`, e.g. `graphene.Field`
            description.append(original_description)
        elif original_description := getattr(field, "kwargs", {}).get("description"):
            # `field` was of `UnmountedType` e.g. `graphene.List`
            description.append(original_description)

        if tuple(inspect.signature(resolver).parameters) == ("root", "info", "id"):
            description.append(api_descriptions.DETAIL_QUERY)
        elif resolver.__name__.startswith("resolve_autocomplete_"):
            description.append(api_descriptions.AUTOCOMPLETE_QUERY)

        if resolver.__doc__:
            description.append(inspect.cleandoc(resolver.__doc__))

        if getattr(resolver, "login_required", False):
            description.append(api_descriptions.AUTH_REQUIRED)

        try:
            # Ignore: It's fine that `.get("return")` might not be a class here,
            #   we let it fail and catch the exception.
            if issubclass(get_type_hints(resolver).get("return"), PaginationMixin):  # type: ignore[arg-type]
                description.append(api_descriptions.PAGINATED)
        except TypeError:
            pass  # Was not a class

        return "\n\n".join(description)


class SkoleObjectType(graphene.ObjectType, metaclass=SkoleObjectTypeMeta):
    """Base model for all GraphQL object types."""


class SkoleDjangoObjectType(
    graphene_django.DjangoObjectType, metaclass=SkoleObjectTypeMeta
):
    """Base model for all graphene-django Django object types."""

    class Meta:
        # `DjangoObjectType` raises an error if `model` has not been set.
        # *This* `model` value is not actually used anywhere. The subclasses need to
        # define their own `Meta.model` and otherwise graphene-django will error out.
        model = User


@validate_is_first_inherited
class SkoleCreateUpdateMutationMixin(metaclass=SkoleObjectTypeMeta):
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

    login_required: ClassVar[bool] = False
    verification_required: ClassVar[bool] = False

    # Defined here to add the default value.
    errors = graphene.List(ErrorType, default_value=[])

    @classmethod
    def get_form_kwargs(
        cls, root: None, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        kwargs = super().get_form_kwargs(root, info, **input)
        kwargs["request"] = info.context
        return kwargs

    @classmethod
    def mutate(cls: Type[M], root: None, info: ResolveInfo, **input: JsonDict) -> M:
        user = info.context.user

        if cls.login_required or cls.verification_required:
            if not user.is_authenticated:
                # Ignore: `errors` is valid arg in subclasses.
                return cls(errors=MutationErrors.AUTH_REQUIRED)  # type: ignore[call-arg]

        user = cast(User, user)

        if cls.verification_required:
            if not user.verified:
                # Ignore: `errors` is valid arg in subclasses.
                return cls(errors=MutationErrors.VERIFICATION_REQUIRED)  # type: ignore[call-arg]

        return super().mutate(root, info, **input)


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
        return_field_name = "success_message"
        only_fields = ("id",)

    @classmethod
    def perform_mutate(
        cls, form: SkoleUpdateModelForm, info: ResolveInfo
    ) -> SkoleDeleteMutationMixin:
        form.instance.soft_delete()
        return super().perform_mutate(form, info)
