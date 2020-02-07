from django import forms

from api.utils.common import TargetMixin
from app.utils.dummy_model import DummyModel


class DeleteObjectForm(forms.ModelForm, TargetMixin):
    comment_id = forms.IntegerField(required=False)
    resource_id = forms.IntegerField(required=False)
    resource_part_id = forms.IntegerField(required=False)
    vote_id = forms.IntegerField(required=False)

    class Meta:
        model = DummyModel
        fields = ("comment_id", "resource_id", "resource_part_id", "vote_id")
