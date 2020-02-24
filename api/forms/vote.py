from django import forms

from api.utils.forms import TargetForm
from core.models import Vote


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
