from pathlib import Path

import requests
from django import forms
from django.conf import settings
from django.core.files.base import ContentFile, File
from django.core.files.uploadedfile import UploadedFile

from skole.utils.constants import ValidationErrors


def convert_to_pdf(file: UploadedFile) -> File:
    path = Path(file.name)

    if path.suffix == ".pdf" or not settings.CLOUDMERSIVE_API_KEY:
        # No need to make an API call if the file is already a pdf,
        # the contents of this file will still validated so nothing
        # bad should be able to sneak through.

        # Someone also might not want to bother setting the API key when developing,
        # so let's not break the whole functionality just because it's not set.

        # We also set the key to be None during tests to avoid calling the API.
        return file

    assert "pytest" not in __import__("sys").modules, "Shouldn't be called from tests!"

    res = requests.post(
        url="https://api.cloudmersive.com/convert/autodetect/to/pdf",
        files={"file": file},
        headers={"Apikey": settings.CLOUDMERSIVE_API_KEY},
    )
    if res.status_code == 200:
        return ContentFile(res.content, f"{path.stem}.pdf")

    raise forms.ValidationError(ValidationErrors.COULD_NOT_CONVERT_FILE.format("PDF"))
