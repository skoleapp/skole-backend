from typing import List

import magic
from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class ValidateFileSizeAndType:
    """A nice way to have validators which take arguments.

    Taken from: https://stackoverflow.com/a/25768034
    """

    def __init__(self, limit: float, types: List[str]) -> None:
        """
        Args:
            limit: The maximum allowed file size in MB
            types: List of allowed file types. Values should be from:
                https://www.iana.org/assignments/media-types/media-types.xhtml
        """
        if limit <= 0:
            raise ValueError("Limit has to be > 0.")
        if types == []:
            raise ValueError("Cannot have an empty list of file types.")
        self.limit = limit
        self.types = types

    def __call__(self, file: FieldFile) -> None:
        # We multiply by 1_000_000 to convert megabytes to bytes.
        if file.size > 1_000_000 * self.limit:
            raise ValidationError(
                _("File is too large, maximum allowed is {}MB").format(self.limit)
            )

        # Reading the first 1024 bytes will be enough to determine the file type.
        file_type = magic.from_buffer(file.read(1024), mime=True)
        if file_type not in self.types:
            raise ValidationError(
                _("Invalid file type, allowed types are: {}").format(
                    ", ".join(self.types)
                )
            )
