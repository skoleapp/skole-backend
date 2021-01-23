import mimetypes
from collections.abc import Collection
from pathlib import Path

import magic
from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile
from django.utils.deconstruct import deconstructible

from skole.utils.constants import ValidationErrors


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
            raise ValidationError(ValidationErrors.FILE_TOO_LARGE.format(self.limit))

        # Reading the first 2048 bytes should be enough
        # to determine the file type: https://github.com/ahupp/python-magic#usage
        file_type = magic.from_buffer(file.read(2048), mime=True)
        if file_type not in self.mimes:
            raise ValidationError(
                ValidationErrors.INVALID_FILE_TYPE.format(self.allowed_types_text)
            )

        file_extension = Path(file.name).suffix.lower()
        if file_extension not in mimetypes.guess_all_extensions(file_type):
            raise ValidationError(ValidationErrors.INVALID_FILE_EXTENSION)
