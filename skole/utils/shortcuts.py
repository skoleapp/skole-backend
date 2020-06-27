from typing import Optional, Type, TypeVar, Union

from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.db import models

from skole.utils.types import ID

T = TypeVar("T", bound=models.Model)


def get_obj_or_none(model: Type[T], pk: ID = None) -> Optional[T]:
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


def full_refresh_from_db(instance: T, /) -> T:
    """Return the same object instance but re-query it from the database.

    This is like Django's `refresh_from_db,` but this also recalculates the values of
    `get_queryset` annotations and aggregations.
    """
    return instance.__class__.objects.get(pk=instance.pk)


def validate_is_first_inherited(parent: type, subclass: type) -> None:
    """Validate that the first inherited class of `subclass` is `parent`.

    Can be used in any class's __init_subclass__ method to validate that the class in
    question is the first class that is ever inherited.

    Examples:
        >>> class Foo:
        ...     def __init_subclass__(cls) -> None:
        ...         validate_is_first_inherited(Foo, cls)
        ...         super().__init_subclass__()
        >>> class Bar: pass
        >>> class Ok1(Foo, Bar): pass
        >>> class Ok2(Foo): pass
        >>> class Ok3(Ok2): pass
        >>> class Fail(Bar, Foo): pass
        Traceback (most recent call last):
            ...
        TypeError: Foo needs to be the first inherited class.
    """
    assert issubclass(subclass, parent)

    while True:
        try:
            if subclass.__bases__[0] is parent:
                return
        except (AttributeError, IndexError):
            break
        subclass = subclass.__bases__[0]

    raise TypeError(f"{parent.__name__} needs to be the first inherited class.")
