from django import forms

from api.utils.common import TargetForm
from app.models import Comment


class CreateUpdateCommentForm(TargetForm):
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
