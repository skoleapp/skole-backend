import datetime
from typing import Union

from django import forms
from django.core.files import File

from skole.models import Resource
from skole.utils.files import clean_file_field, clean_metadata, convert_to_pdf

from .base import SkoleModelForm, SkoleUpdateModelForm


class CreateResourceForm(SkoleModelForm):
    file = forms.CharField(required=True)

    class Meta:
        model = Resource
        fields = ("title", "file", "resource_type", "course", "date")

    def clean_file(self) -> Union[File, str]:
        file, __ = clean_file_field(
            form=self,
            field_name="file",
            created_file_name="resource",
            conversion_func=convert_to_pdf,
        )
        return file

    def clean_date(self) -> datetime.date:
        # If the user did provide a date for the resource, use that,
        # otherwise just use the default from the model.
        return (
            self.cleaned_data.get("date")
            or Resource._meta.get_field(  # pylint: disable=protected-access
                "date"
            ).get_default()
        )

    def save(self, commit: bool = True) -> Resource:
        assert self.request is not None

        # Should always be authenticated here, so fine to raise `ValueError` here
        # if we accidentally try to set `instance.user` to an `AnonymousUser`.
        self.instance.user = self.request.user
        self.instance = super().save(commit)

        # We on purpose want to clean the metadata of files that have been converted
        # with Cloudmersive also, so that they can leave no nasty data to our files.
        clean_metadata(self.instance.file)
        return self.instance


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


class DownloadResourceForm(SkoleModelForm):
    class Meta:
        model = Resource
        fields = ("id",)

    def save(self, commit: bool = True) -> Resource:
        return Resource.objects.increment_downloads(self.instance)
