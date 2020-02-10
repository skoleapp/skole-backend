from django import forms

from api.utils.common import TargetForm
from app.models import Comment


class CreateCommentForm(TargetForm):
    class Meta:
        model = Comment
        fields = (
            "text",
            "attachment",
            "course_id",
            "resource_id",
            "resource_part_id",
            "comment_id",
        )


class UpdateCommentForm(forms.ModelForm):
    comment_id = forms.IntegerField()
    attachment = forms.CharField(required=False)

    class Meta:
        model = Comment
        fields = ("comment_id", "text", "attachment")
