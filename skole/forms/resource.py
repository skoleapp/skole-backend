from typing import Union

from django import forms
from django.core.files.uploadedfile import UploadedFile

from skole.models import Resource
from skole.utils.forms import DeleteObjectForm
from skole.utils.shortcuts import clean_file_field


class CreateResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ("title", "file", "resource_type", "course", "date")

    def clean_file(self) -> Union[UploadedFile, str]:
        return clean_file_field(self, "file")


class UpdateResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ("id", "title", "resource_type", "date")

    clean_file = CreateResourceForm.clean_file


class DeleteResourceForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Resource
