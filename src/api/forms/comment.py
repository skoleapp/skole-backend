from django import forms
from mypy.types import JsonDict

from api.utils.common import clean_target
from app.models import Comment


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            "text",
            "attachment",
            "course",
            "resource",
            "resource_part",
            "comment",
        )

    def clean(self) -> JsonDict:
        return clean_target(
            self.cleaned_data, "course", "resource", "resource_part", "comment"
        )


class UpdateCommentForm(forms.ModelForm):
    comment_id = forms.IntegerField()
    attachment = forms.CharField(required=False)

    class Meta:
        model = Comment
        fields = ("comment_id", "text", "attachment")
