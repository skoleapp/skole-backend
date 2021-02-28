from typing import Any, Union, cast

from django import forms
from django.core.files import File

from skole.models import Comment
from skole.utils.constants import ValidationErrors
from skole.utils.files import clean_file_field

from .base import SkoleModelForm, SkoleUpdateModelForm


class _BaseCreateUpdateCommentForm(SkoleModelForm):
    def clean_attachment(self) -> Union[File, str]:
        attachment = clean_file_field(
            form=cast(SkoleModelForm, self),
            field_name="attachment",
            created_file_name="attachment",
        )

        if self.cleaned_data["text"] == "" and attachment == "":
            raise forms.ValidationError(ValidationErrors.COMMENT_EMPTY)

        return attachment


class CreateCommentForm(_BaseCreateUpdateCommentForm, SkoleModelForm):
    class Meta:
        model = Comment
        fields = (
            "user",
            "text",
            "attachment",
            "course",
            "resource",
            "comment",
            "school",
        )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.request:
            if not self.request.user.is_authenticated or not self.request.user.verified:
                self.fields.pop("attachment")

    def save(self, commit: bool = True) -> Comment:
        assert self.request is not None

        # Check that the user making the request is the same as the user passed in the form.
        # Only if they match, use the user from the request as the author of the comment.
        if self.request.user == self.cleaned_data.get("user"):
            self.instance.user = self.request.user
        else:
            self.instance.user = None

        return super().save(commit)


class UpdateCommentForm(_BaseCreateUpdateCommentForm, SkoleUpdateModelForm):
    class Meta:
        model = Comment
        fields = ("id", "text", "attachment")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.request:
            if not self.request.user.is_authenticated or not self.request.user.verified:
                self.fields.pop("attachment")


class DeleteCommentForm(SkoleUpdateModelForm):
    class Meta:
        model = Comment
        fields = ("id",)
