from django import forms

from skole.models import Vote
from skole.utils.forms import TargetForm


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
