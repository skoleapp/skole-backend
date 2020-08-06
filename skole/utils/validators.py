import mimetypes
from pathlib import Path
from typing import Sequence, Tuple

import magic
from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile
from django.utils.deconstruct import deconstructible

from skole.utils.constants import ValidationErrors


@deconstructible
class ValidateFileSizeAndType:
    """A nice way to have validators which take arguments.

    Source: https://stackoverflow.com/a/25768034
    """

    def __init__(self, limit: float, types: Sequence[Tuple[str, str]]) -> None:
        """
        Args:
            limit: The maximum allowed file size in MB
            types: Sequence of allowed file types as (mime, human_friendly_name) pairs.
                Mime values should be from: https://www.iana.org/assignments/media-types/media-types.xhtml
        """
        if limit <= 0:
            raise ValueError("Limit has to be > 0.")
        if not types:
            raise ValueError("Need to have at least one allowed file type.")
        self.limit = limit
        self.mimes, human_friendly = (set(seq) for seq in zip(*types))
        self.allowed_types = ", ".join(sorted(human_friendly))

    def __call__(self, file: FieldFile) -> None:
        # We multiply by 1_000_000 to convert megabytes to bytes.
        if file.size > 1_000_000 * self.limit:
            raise ValidationError(ValidationErrors.FILE_TOO_LARGE.format(self.limit))

        # Reading the first 1024 bytes will be more than enough to determine the type.
        file_type = magic.from_buffer(file.read(1024), mime=True)
        if file_type not in self.mimes:
            raise ValidationError(
                ValidationErrors.INVALID_FILE_TYPE.format(self.allowed_types)
            )

        file_extension = Path(file.name).suffix.lower()
        if file_extension not in mimetypes.guess_all_extensions(file_type):
            raise ValidationError(ValidationErrors.INVALID_FILE_EXTENSION)
