from typing import Any, Union, cast

from django import forms
from django.core.files import File

from skole.models import Comment
from skole.types import JsonDict
from skole.utils.constants import ValidationErrors
from skole.utils.files import clean_file_field
from skole.utils.shortcuts import validate_single_target

from .base import SkoleModelForm, SkoleUpdateModelForm


class _CommentFormMixin:

    attachment = forms.CharField(required=False)

    def clean_attachment(self) -> Union[File, str]:
        attachment = clean_file_field(
            form=cast(forms.ModelForm, self),
            field_name="attachment",
            created_file_name="attachment",
        )

        # Ignore: Will be defined in subclasses.
        if self.cleaned_data["text"] == "" and attachment == "":  # type: ignore[attr-defined]
            raise forms.ValidationError(ValidationErrors.COMMENT_EMPTY)

        return attachment


class CreateCommentForm(_CommentFormMixin, SkoleModelForm):
    class Meta:
        model = Comment
        fields = ("text", "attachment", "course", "resource", "comment")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.request:
            if not self.request.user.is_authenticated or not self.request.user.verified:
                self.fields.pop("attachment")

    def clean(self) -> JsonDict:
        data = super().clean()
        validate_single_target(data, "course", "comment", "resource")
        return data

    def save(self, commit: bool = True) -> Comment:
        assert self.request is not None
        if self.request.user.is_authenticated:
            self.instance.user = self.request.user
        return super().save(commit)


class UpdateCommentForm(_CommentFormMixin, SkoleUpdateModelForm):
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
