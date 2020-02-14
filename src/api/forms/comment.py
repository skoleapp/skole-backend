from api.utils.common import TargetForm
from app.models import Comment


class CreateUpdateCommentForm(TargetForm):
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
