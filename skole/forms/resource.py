import datetime
from typing import Any, Optional, Union

from django import forms
from django.contrib.auth import get_user_model
from django.core.files import File

from skole.models import Author, Resource
from skole.utils.files import clean_file_field, convert_to_pdf

from .base import SkoleModelForm, SkoleUpdateModelForm


class _BaseCreateUpdateResourceForm(SkoleModelForm):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.fields["author"] = Author.formfield("name", required=False)

    def clean_author(self) -> Optional[Author]:
        """
        If this it set this to the current user's username, don't set it at all.

        When the author is null, the frontend will know to just show a link to the
        `user` field's value.
        """
        assert self.request is not None

        cleaned_author = self.cleaned_data["author"]
        if cleaned_author:
            user = (
                get_user_model().objects.filter(username__iexact=cleaned_author).first()
            )
            if user:
                return Author.objects.get_or_create(user=user)[0]
            return Author.objects.get_or_create(name=cleaned_author)[0]
        return None

    def save(self, commit: bool = True) -> Resource:
        assert self.request is not None

        # Should always be authenticated here, so fine to raise `ValueError` here
        # if we accidentally try to set `instance.user` to an `AnonymousUser`.
        if not self.instance.user:
            self.instance.user = self.request.user

        return super().save(commit)


class CreateResourceForm(_BaseCreateUpdateResourceForm, SkoleModelForm):
    file = forms.CharField(required=True)

    class Meta:
        model = Resource
        fields = ("title", "file", "resource_type", "course", "date", "author")

    def clean_file(self) -> Union[File, str]:
        return clean_file_field(
            form=self,
            field_name="file",
            created_file_name="resource",
            conversion_func=convert_to_pdf,
        )

    def clean_date(self) -> datetime.date:
        # pylint: disable=protected-access

        # If the user did provide a date for the resource, use that,
        # otherwise just use the default from the model.
        return (
            self.cleaned_data.get("date")
            or Resource._meta.get_field("date").get_default()
        )


class UpdateResourceForm(_BaseCreateUpdateResourceForm, SkoleUpdateModelForm):
    class Meta:
        model = Resource
        fields = ("id", "title", "resource_type", "date", "author")

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
