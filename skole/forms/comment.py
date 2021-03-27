from typing import Any, Optional, cast

from django import forms

from skole.forms.base import SkoleModelForm, SkoleUpdateModelForm
from skole.models import Comment, User
from skole.utils.constants import ValidationErrors
from skole.utils.files import clean_file_field, convert_to_pdf


class _BaseCreateUpdateCommentForm(SkoleModelForm):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.request:
            if not self.request.user.is_authenticated or not self.request.user.verified:
                self.fields.pop("file")
                self.fields.pop("image")

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        if len(self.files) > 1:
            raise forms.ValidationError(ValidationErrors.COMMENT_ONE_FILE)

        if "file" in self.fields:
            cleaned_data["file"] = clean_file_field(
                form=cast(SkoleModelForm, self),
                field_name="file",
                created_file_name="comment_file",
                conversion_func=convert_to_pdf,
            )
        if "image" in self.fields:
            cleaned_data["image"] = clean_file_field(
                form=cast(SkoleModelForm, self),
                field_name="image",
                created_file_name="comment_image",
            )

        if not any(cleaned_data.get(key) for key in ("text", "file", "image")):
            raise forms.ValidationError(ValidationErrors.COMMENT_EMPTY)

        return cleaned_data


class CreateCommentForm(_BaseCreateUpdateCommentForm, SkoleModelForm):
    class Meta:
        model = Comment
        fields = (
            "user",
            "text",
            "file",
            "image",
            "thread",
            "comment",
        )

    def clean_user(self) -> Optional[User]:
        user = self.cleaned_data["user"]

        assert self.request is not None

        # Check that the user making the request is the same as the user passed in the form.
        # Only if they match, use the user from the request as the author of the comment.
        if user and self.request.user != user:
            raise forms.ValidationError(ValidationErrors.INVALID_COMMENT_AUTHOR)

        return user


class UpdateCommentForm(_BaseCreateUpdateCommentForm, SkoleUpdateModelForm):
    class Meta:
        model = Comment
        fields = ("id", "text", "file", "image")


class DeleteCommentForm(SkoleUpdateModelForm):
    class Meta:
        model = Comment
        fields = ("id",)
