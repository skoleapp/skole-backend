from django import forms
from mypy.types import JsonDict
from app.models import Vote
from api.utils.common import TargetMixin


class CreateVoteForm(forms.ModelForm, TargetMixin):
    status = forms.IntegerField()
    comment = forms.IntegerField(required=False)
    course = forms.IntegerField(required=False)
    resource = forms.IntegerField(required=False)

    class Meta:
        model = Vote
        fields = (
            "status",
            "comment",
            "course",
            "resource",
        )
