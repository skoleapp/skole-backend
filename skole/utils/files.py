import datetime
import json
import logging
import os
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Optional, Union

import libmat2.parser_factory
import requests
from django import forms
from django.conf import settings
from django.core.files.base import ContentFile, File
from django.core.files.storage import default_storage

from skole.forms.base import SkoleModelForm
from skole.utils.constants import ValidationErrors

logger = logging.getLogger(__name__)


def clean_file_field(
    form: SkoleModelForm,
    field_name: str,
    created_file_name: str,
    conversion_func: Optional[Callable[[File], File]] = None,
) -> Union[File, str]:
    """
    Use in a ModelForm to conveniently handle FileField clearing and updating.

    Args:
        form: The form that the file field belongs to.
        field_name: The name of the form field where the file is.
        created_file_name: If a new file was uploaded, this will become the name of it.
        conversion_func: Optional converter function to pass the file through,
            when the value has changed.

    Returns:
        A two tuple of the new field value and the operation that was done to the field.

    Raises:
        ValidationError: If the form field was marked as required and this
            function's return value would be empty.

    See `CreateResourceForm.clean_file` for example usage.
    """
    assert form.files is not None
    file: Union[File, str]

    assert form.request
    files_map = json.loads(form.request.POST.get("map", "{}"))

    if files_map.get("1", [""])[0].endswith(f".{field_name}") and (
        uploaded := form.files.get("1")
    ):
        # New value for the field.
        file = conversion_func(uploaded) if conversion_func is not None else uploaded
        file = _clean_metadata(file)
        file.name = created_file_name + Path(file.name).suffix
    elif not form.data.get(field_name):
        # Field value deleted (frontend submitted "" or null value).
        # We can't access this from `cleaned_data`, since the file is actually put
        # there automatically by Django, because normally the file is only meant to be
        # cleared by submitting a "false" value from the ClearableFileInput's checkbox.
        file = ""
    else:
        # Field not modified.
        file = getattr(form.instance, field_name)

    if not file and form.fields[field_name].required:
        raise forms.ValidationError(
            form.fields[field_name].error_messages["required"], code="required"
        )

    return file


def convert_to_pdf(file: File) -> File:
    """Convert the passed file to PDF format using Cloudmersive's conversion API."""
    path = Path(file.name)

    if path.suffix == ".pdf" or not settings.CLOUDMERSIVE_API_KEY:
        # No need to make an API call if the file is already a pdf.
        # The contents of the file will still be validated so nothing
        # bad should be able to sneak through.
        #
        # Someone also might not want to bother setting the API key when developing,
        # so let's not break the whole functionality just because it's not set.
        #
        # We also set the key to be None during tests to avoid calling the API.
        return file

    assert "pytest" not in __import__("sys").modules or isinstance(
        requests.post, __import__("unittest.mock").mock.MagicMock
    ), "Shouldn't be called from tests without first mocking `requests.post`!"

    try:
        res = requests.post(
            url="https://api.cloudmersive.com/convert/autodetect/to/pdf",
            files={"file": file},
            headers={"Apikey": settings.CLOUDMERSIVE_API_KEY},
        )
    except requests.RequestException:
        logger.exception("Encountered an exception when calling Cloudmersive's API.")
    else:
        if res.status_code == 200:
            return ContentFile(res.content, f"{path.stem}.pdf")
        else:
            logger.error(
                f"Received an error from Cloudmersive API, "
                f"status code: {res.status_code}, content: {res.content!r}"
            )

    raise forms.ValidationError(ValidationErrors.COULD_NOT_CONVERT_FILE.format("PDF"))


def _clean_metadata(file: File) -> File:
    """
    Clean the metadata of the file.

    `libmat2` only supports cleaning files that are saved on disk, because it relies
    on exiftool for image cleaning. `file` is currently just in memory, so we need
    to use a temporary file. We also cannot just delay calling this until the file
    gets saved to the disk, since `S3Storage` doesn't support accessing files with an
    absolut path.

    References:
         https://0xacab.org/jvoisin/mat2/-/blob/46b3ae16729c3f18c4bfebccf928e422a2e5c4f4/mat2#L123
    """
    with tempfile.NamedTemporaryFile(suffix=Path(file.name).suffix) as temp:
        temp.write(file.read())
        temp.seek(0)

        parser, file_type = libmat2.parser_factory.get_parser(temp.name)
        if not parser:
            # Most likely the file didn't have an extension and that's why it failed.
            # It's fine to just return the unchanged file here, since model validators
            # will check its type ones more and return a proper user-facing error message.
            logger.error(f"Could not get a libmat2 parser for filetype `{file_type}`")
            return file

        # We use lightweight mode to avoid lowering the quality of uploaded files.
        # This can leave some minor metadata in place, but our use case isn't too strict.
        parser.lightweight_cleaning = True

        parser.remove_all()  # `temp` has to exist until here.

    try:
        with open(parser.output_filename, "rb") as cleaned:
            file = ContentFile(cleaned.read(), file.name)
            os.remove(parser.output_filename)
    except FileNotFoundError:
        # The cleaning of the file failed. Could happen for example because a PNG file
        # was named as `foo.jpeg`. Fine to return the file here unaltered, since model
        # validators will handle the rest.
        logger.exception(f"Failed to open the cleaned file `{parser.output_filename}`")

    return file


@contextmanager
def override_s3_file_age(age: datetime.timedelta) -> Generator[None, None, None]:
    if settings.DEBUG:
        yield
        return  # No S3 in the dev env.

    initial = default_storage.settings.AWS_S3_MAX_AGE_SECONDS
    default_storage.settings.AWS_S3_MAX_AGE_SECONDS = int(age.total_seconds())
    try:
        yield
    finally:
        default_storage.settings.AWS_S3_MAX_AGE_SECONDS = initial
