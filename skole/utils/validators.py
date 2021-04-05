import mimetypes
from collections.abc import Collection
from pathlib import Path
from typing import Any, TypeVar

import magic
from django import forms
from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile
from django.utils.deconstruct import deconstructible

from skole.types import JsonDict
from skole.utils.constants import Errors

T = TypeVar("T")


@deconstructible
class ValidateFileSizeAndType:
    """Use as a field validator to validate the the file type and size."""

    def __init__(self, limit: float, types: Collection[tuple[str, str]]) -> None:
        """
        Args:
            limit: The maximum allowed file size in MB.
            types: Allowed file types as (mimetype, human_friendly_name) pairs.
                Mime values should be from: https://www.iana.org/assignments/media-types/media-types.xhtml
        """
        if limit <= 0:
            raise ValueError("Limit has to be > 0.")
        if not types:
            raise ValueError("Need to have at least one allowed file type.")
        self.limit = limit
        self.mimes, human_friendlies = (set(seq) for seq in zip(*types))
        self.allowed_types_text = ", ".join(sorted(human_friendlies))

    def __call__(self, file: FieldFile) -> None:
        # We multiply by 1_000_000 to convert megabytes to bytes.
        if file.size > 1_000_000 * self.limit:
            raise ValidationError(Errors.FILE_TOO_LARGE.format(self.limit))

        # Reading the first 2048 bytes should be enough
        # to determine the file type: https://github.com/ahupp/python-magic#usage
        file_type = magic.from_buffer(file.read(2048), mime=True)
        if file_type not in self.mimes:
            raise ValidationError(
                Errors.INVALID_FILE_TYPE.format(self.allowed_types_text)
            )

        file_extension = Path(file.name).suffix.lower()
        if file_extension not in mimetypes.guess_all_extensions(file_type):
            raise ValidationError(Errors.INVALID_FILE_EXTENSION)


def validate_is_first_inherited(decorated: type[T]) -> type[T]:
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

    def init_subclass_with_validation(cls: type[Any]) -> None:
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
        raise forms.ValidationError(Errors.MUTATION_INVALID_TARGET)
    return found[0]
