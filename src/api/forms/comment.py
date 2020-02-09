from django import forms

from api.utils.common import TargetMixin
from app.models import Comment


class CreateCommentForm(TargetMixin, forms.ModelForm):
    course_id = forms.IntegerField(required=False)
    resource_id = forms.IntegerField(required=False)
    resource_part_id = forms.IntegerField(required=False)
    comment_id = forms.IntegerField(required=False)

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
