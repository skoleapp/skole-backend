from typing import Any, Type, TypeVar

from django import forms
from django.db.models import Model

from skole.types import JsonDict
from skole.types._aliases import FormError
from skole.utils.constants import ValidationErrors

T = TypeVar("T")
M = TypeVar("M", bound=Model)


def full_refresh_from_db(instance: M, /) -> M:
    """
    Return the same object instance but re-query it from the database.

    This is like Django's `refresh_from_db,` but this also recalculates the values of
    `get_queryset` annotations and aggregations.
    """
    return instance.__class__.objects.get(pk=instance.pk)


def validate_is_first_inherited(decorated: Type[T]) -> Type[T]:
    """
    Add as a decorator to a class to ensure that it's the first class ever inherited.

    Caution: Does not work when a class has overridden __init_subclass__ in a way
    that does not call super(). This is the case with
    all graphene types: https://github.com/graphql-python/graphene/issues/1233

    Examples:
        >>> @validate_is_first_inherited
        ... class Foo:
        ...     pass
        >>> class Bar: pass
        >>> class Ok1(Foo, Bar): pass
        >>> class Ok2(Foo): pass
        >>> class Ok3(Ok2): pass
        >>> class Fail(Bar, Foo): pass
        Traceback (most recent call last):
            ...
        TypeError: Foo needs to be the first inherited class.
    """

    def init_subclass_with_validation(cls: Type[Any]) -> None:
        super(decorated, cls).__init_subclass__()
        found = False
        while True:
            try:
                if cls.__bases__[0] is decorated:
                    found = True
                    break
            except (AttributeError, IndexError):
                break
            cls = cls.__bases__[0]
        if not found:
            raise TypeError(
                f"{decorated.__name__} needs to be the first inherited class."
            )

    setattr(decorated, "__init_subclass__", classmethod(init_subclass_with_validation))
    return decorated


def validate_single_target(data: JsonDict, *keys: str) -> Any:
    """
    Validate that exactly one of the `keys` in `data` have a non None value.

    Returns:
        The found value on success.

    Raises:
         ValidationError: if found 0 values or more than 1 values.
    """
    found = [value for key in keys if (value := data.get(key)) is not None]
    if len(found) != 1:
        raise forms.ValidationError(ValidationErrors.MUTATION_INVALID_TARGET)
    return found[0]


E = TypeVar("E", bound=FormError)


def format_form_error(error: E, *args: Any, **kwargs: Any) -> E:
    error[0]["messages"][0] = error[0]["messages"][0].format(*args, **kwargs)
    return error
