from typing import Union

from django import forms
from django.core.files import File

from skole.models import Resource
from skole.utils.cloudmersive import convert_to_pdf
from skole.utils.forms import DeleteObjectForm
from skole.utils.shortcuts import clean_file_field


class CreateResourceForm(forms.ModelForm):
    file = forms.CharField(required=False)

    class Meta:
        model = Resource
        fields = ("title", "file", "resource_type", "course", "date")

    def clean_file(self) -> Union[File, str]:
        return clean_file_field(self, "file", conversion_func=convert_to_pdf)


class UpdateResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ("id", "title", "resource_type", "date")


class DeleteResourceForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Resource
