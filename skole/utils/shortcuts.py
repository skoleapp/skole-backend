from typing import Any, Callable, Optional, Type, TypeVar, Union

from django import forms
from django.core.files import File
from django.db import models

from skole.utils.types import ID

T = TypeVar("T")
M = TypeVar("M", bound=models.Model)


def get_obj_or_none(model: Type[M], pk: ID = None) -> Optional[M]:
    """Used as a helper function to return None instead of raising a GraphQLError."""

    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None


def clean_file_field(
    form: forms.ModelForm,
    field_name: str,
    conversion_func: Optional[Callable[[File], File]] = None,
) -> Union[File, str]:
    """Use in a ModelForm to conveniently handle FileField clearing and updating.

    Args:
        form: The form that the file field belongs to.
        field_name: The name of the form field where the file is.
        conversion_func: Optional converter function to pass the file through,
            when the value has changed.

    See `CreateResourceForm.clean_file` for example usage.
    """
    assert form.files is not None

    if file := form.files.get("1"):
        # New value for the field.
        return conversion_func(file) if conversion_func is not None else file
    elif form.cleaned_data[field_name] == "":
        # Field value deleted.
        return ""
    else:
        # Field not modified.
        return getattr(form.instance, field_name)


def full_refresh_from_db(instance: M, /) -> M:
    """Return the same object instance but re-query it from the database.

    This is like Django's `refresh_from_db,` but this also recalculates the values of
    `get_queryset` annotations and aggregations.
    """
    return instance.__class__.objects.get(pk=instance.pk)


def validate_is_first_inherited(decorated: Type[T]) -> Type[T]:
    """Add as a decorator to a class to ensure that it's the first class ever inherited.

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
