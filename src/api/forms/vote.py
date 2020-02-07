from django import forms
from mypy.types import JsonDict
from app.models import Vote
from api.utils.common import TargetMixin


class CreateVoteForm(forms.ModelForm, TargetMixin):
    status = forms.IntegerField()
    comment_id = forms.IntegerField(required=False)
    course_id = forms.IntegerField(required=False)
    resource_id = forms.IntegerField(required=False)

    class Meta:
        model = Vote
        fields = (
            "status",
            "comment_id",
            "course_id",
            "resource_id",
        )
