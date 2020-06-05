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


def refresh_all_fields(instance: T, /) -> T:
    """Return the same object instance but re-query it from the database.

    This is like Django's `refresh_from_db,` but this also recalculates the values of
    `get_queryset` annotations and aggregations.
    """
    return instance.__class__.objects.get(pk=instance.pk)
