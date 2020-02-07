from django import forms
from mypy.types import JsonDict
from app.models import Vote
from api.utils.common import TargetMixin
from app.utils.dummy_model import DummyModel


class DeleteObjectForm(forms.ModelForm, TargetMixin):
    comment = forms.IntegerField(required=False)
    resource = forms.IntegerField(required=False)
    resource_part = forms.IntegerField(required=False)
    vote = forms.IntegerField(required=False)

    class Meta:
        model = DummyModel
        fields = ("comment", "resource", "resource_part", "vote")
