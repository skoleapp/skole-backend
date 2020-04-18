from django import forms

from api.utils.forms import DeleteObjectForm, TargetForm
from core.models import Comment


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

    def clean_attachment(self) -> str:
        # Ignore: Mypy considers files as optional but they're always at least an empty MultiValueDict.
        if attachment := self.files.get("1", None):  # type: ignore [union-attr]
            return attachment
        else:
            return self.cleaned_data["attachment"]


class UpdateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("id", "text", "attachment")

    clean_attachment = CreateCommentForm.clean_attachment


class DeleteCommentForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Comment
