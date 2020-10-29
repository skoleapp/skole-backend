import os
from pathlib import Path
from typing import Callable, Optional, Tuple, Union

import libmat2.parser_factory
import requests
from django import forms
from django.conf import settings
from django.core.files.base import ContentFile, File

from skole.utils.constants import FieldOperation, ValidationErrors


def clean_file_field(
    form: forms.ModelForm,
    field_name: str,
    created_file_name: str,
    conversion_func: Optional[Callable[[File], File]] = None,
) -> Tuple[Union[File, str], FieldOperation]:
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

    if uploaded := form.files.get("1"):
        # New value for the field.
        file = conversion_func(uploaded) if conversion_func is not None else uploaded
        file.name = created_file_name + Path(file.name).suffix
        operation = FieldOperation.NEW_VALUE
    elif not form.data[field_name]:
        # Field value deleted (frontend submitted "" or null value).
        # We can't access this from `cleaned_data`, since the file is actually put
        # there automatically by Django, because normally the file is only meant to be
        # cleared by submitting a "false" value from the ClearableFileInput's checkbox.
        file = ""
        operation = FieldOperation.CLEARED
    else:
        # Field not modified.
        file = getattr(form.instance, field_name)
        operation = FieldOperation.UNCHANGED

    if not file and form.fields[field_name].required:
        raise forms.ValidationError(
            form.fields[field_name].error_messages["required"], code="required"
        )

    return file, operation


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

    res = requests.post(
        url="https://api.cloudmersive.com/convert/autodetect/to/pdf",
        files={"file": file},
        headers={"Apikey": settings.CLOUDMERSIVE_API_KEY},
    )
    if res.status_code == 200:
        return ContentFile(res.content, f"{path.stem}.pdf")

    raise forms.ValidationError(ValidationErrors.COULD_NOT_CONVERT_FILE.format("PDF"))


def clean_metadata(filepath: str) -> None:
    """
    Do on inplace cleaning of metadata of the file stored `filepath`.

    Only works for files that are saved on disk, because of `libmat2`'s limitations.

    Notes:
        This could potentially be run asynchronously in the future, because it's not
        in way critical that the file gets cleaned *immediately* after it's been
        uploaded. The uploader of the file is most likely the only one to see the file
        in that small span of time and they already know the metadata of their own file.
        This is not super critical though, since this execution only takes ~300ms.

    Reference: https://0xacab.org/jvoisin/mat2/-/blob/46b3ae16729c3f18c4bfebccf928e422a2e5c4f4/mat2#L123
    """
    parser, file_type = libmat2.parser_factory.get_parser(filepath)
    if not parser:
        raise RuntimeError(f"Could not get a libmat2 parser for filetype {file_type}.")

    # We use lightweight mode to avoid lowering the quality of uploaded files.
    # This can leave some minor metadata in place, but our use case isn't too strict.
    parser.lightweight_cleaning = True

    parser.remove_all()

    # Otherwise the cleaned file will appear as resource.cleaned.pdf,
    # but we want it to replace the existing file.
    os.rename(parser.output_filename, filepath)
