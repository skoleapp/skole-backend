from django import forms
from mypy.types import JsonDict

from api.utils.common import clean_target
from app.models import Vote


class CreateVoteForm(forms.ModelForm):
    status = forms.IntegerField()

    class Meta:
        model = Vote
        fields = (
            "status",
            "comment",
            "course",
            "resource",
        )

    def clean(self) -> JsonDict:
        return clean_target(self.cleaned_data, "comment", "course", "resource")
