from django import forms

from api.utils.forms import DeleteObjectForm, TargetForm
from app.models import Vote


class CreateVoteForm(TargetForm):
    status = forms.IntegerField(required=True)

    class Meta:
        model = Vote
        fields = (
            "status",
            "comment",
            "course",
            "resource",
        )


class DeleteVoteForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Vote
