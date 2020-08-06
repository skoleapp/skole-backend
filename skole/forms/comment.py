from typing import Union

from django import forms
from django.core.files import File

from skole.models import Comment
from skole.utils.constants import ValidationErrors
from skole.utils.forms import DeleteObjectForm, TargetForm
from skole.utils.shortcuts import clean_file_field


class _BaseCommentForm(forms.ModelForm):
    attachment = forms.CharField(required=False)

    def clean_attachment(self) -> Union[File, str]:
        attachment = clean_file_field(self, "attachment")

        if self.cleaned_data["text"] == "" and attachment == "":
            raise forms.ValidationError(ValidationErrors.COMMENT_EMPTY)

        return attachment


class CreateCommentForm(TargetForm, _BaseCommentForm):
    class Meta:
        model = Comment
        fields = ("text", "attachment", "course", "resource", "comment")


class UpdateCommentForm(_BaseCommentForm):
    class Meta:
        model = Comment
        fields = ("id", "text", "attachment")


class DeleteCommentForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Comment
