import datetime
from typing import Union

from django import forms
from django.core.files import File

from skole.models import Resource
from skole.utils.cloudmersive import convert_to_pdf
from skole.utils.shortcuts import clean_file_field

from .base import SkoleModelForm, SkoleUpdateModelForm


class CreateResourceForm(SkoleModelForm):
    file = forms.CharField(required=False)

    class Meta:
        model = Resource
        fields = ("title", "file", "resource_type", "course", "date")

    def clean_file(self) -> Union[File, str]:
        return clean_file_field(self, "file", conversion_func=convert_to_pdf)

    def clean_date(self) -> datetime.date:
        # If the user did provide a date for the resource, use that,
        # otherwise just use the default from the model.
        return (
            self.cleaned_data.get("date")
            or Resource._meta.get_field("date").get_default()
        )


class UpdateResourceForm(SkoleUpdateModelForm):
    class Meta:
        model = Resource
        fields = ("id", "title", "resource_type", "date")

    def clean_date(self) -> datetime.date:
        # If a new date wasn't provided, just use the currently set one
        # instead of setting it to None (which would fail).
        return self.cleaned_data.get("date") or self.instance.date


class DeleteResourceForm(SkoleUpdateModelForm):
    class Meta:
        model = Resource
        fields = ("id",)
