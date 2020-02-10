from django import forms

from api.utils.common import TargetForm
from app.models import Vote


class CreateVoteForm(TargetForm):
    status = forms.IntegerField()
    vote_id = forms.IntegerField() # Override to make it required.

    class Meta:
        model = Vote
        fields = (
            "status",
            "comment_id",
            "course_id",
            "resource_id",
        )
