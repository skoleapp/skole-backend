from typing import Union

from django import forms
from django.core.files.uploadedfile import UploadedFile

from skole.models import Comment
from skole.utils.forms import DeleteObjectForm, TargetForm
from skole.utils.shortcuts import clean_file_field


class CreateCommentForm(TargetForm):
    class Meta:
        model = Comment
        fields = (
            "text",
            "attachment",
            "course",
            "resource",
            "comment",
        )

    def clean_attachment(self) -> Union[UploadedFile, str]:
        return clean_file_field(self, "attachment")


class UpdateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("id", "text", "attachment")

    clean_attachment = CreateCommentForm.clean_attachment


class DeleteCommentForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Comment
