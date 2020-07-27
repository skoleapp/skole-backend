from typing import Optional, Type, TypeVar, Union

from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.db import models

from skole.utils.types import ID

M = TypeVar("M", bound=models.Model)
T = TypeVar("T", bound=type)


def get_obj_or_none(model: Type[M], pk: ID = None) -> Optional[M]:
    """Used as a helper function to return None instead of raising a GraphQLError."""

    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None


def clean_file_field(
    form: forms.ModelForm, field_name: str
) -> Union[UploadedFile, str]:
    """Use in a ModelForm to conveniently handle FileField clearing and updating.

    See UpdateUserForm.clean_avatar for example usage.
    """
    assert form.files is not None

    if file := form.files.get("1"):
        # New value for the field.
        return file
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


def validate_is_first_inherited(decorated: T) -> T:
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

    def init_subclass_with_validation(cls: type) -> None:
        # Ignore: even though T is defined with bound=type, Mypy gives the error:
        #   Argument 1 for "super" must be a type object; got "T"
        super(decorated, cls).__init_subclass__()  # type: ignore[misc]
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

    # Ignore: Mypy doesn't like assigning to a method.
    decorated.__init_subclass__ = classmethod(init_subclass_with_validation)  # type: ignore[assignment]
    return decorated
