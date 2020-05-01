from functools import wraps
from typing import Any, Callable, Type, TypeVar

import graphene
from django import forms
from graphql import ResolveInfo

from skole.utils.constants import MutationErrors

T = TypeVar("T", bound=graphene.Mutation)
F = TypeVar("F", bound=forms.ModelForm)


def login_required_mutation(
    func: Callable[[Type[T], F, ResolveInfo], T]
) -> Callable[[Type[T], F, ResolveInfo], T]:
    """Custom decorator for mutations that require authentication."""

    @wraps(func)
    def wrapper(cls: Type[T], root: Any, info: ResolveInfo) -> T:
        assert info.context is not None
        user = info.context.user
        if not user.is_authenticated:
            return cls(errors=MutationErrors.AUTH_REQUIRED)

        return func(cls, root, info)

    return wrapper


def verification_required_mutation(
    func: Callable[[Type[T], F, ResolveInfo], T]
) -> Callable[[Type[T], F, ResolveInfo], T]:
    """Custom decorator for mutations that require verification and authentication."""

    @wraps(func)
    @login_required_mutation
    def wrapper(cls: Type[T], root: Any, info: ResolveInfo) -> T:
        assert info.context is not None
        user = info.context.user
        if not user.verified:
            return cls(errors=MutationErrors.VERIFICATION_REQUIRED)

        return func(cls, root, info)

    return wrapper
