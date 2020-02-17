from api.utils.forms import DeleteObjectForm, TargetForm
from app.models import Comment


class CreateUpdateCommentForm(TargetForm):
    class Meta:
        model = Comment
        fields = (
            "text",
            "attachment",
            "course",
            "resource",
            "comment",
        )


class DeleteCommentForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Comment
