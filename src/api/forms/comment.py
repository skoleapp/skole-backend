from django import forms
from mypy.types import JsonDict
from app.models import Comment
from api.utils.common import TargetMixin


class CreateCommentForm(forms.ModelForm, TargetMixin):
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


class UpdateCommentForm(forms.ModelForm):
    comment_id = forms.IntegerField()
    attachment = forms.CharField(required=False)

    class Meta:
        model = Comment
        fields = ("comment_id", "text", "attachment")
