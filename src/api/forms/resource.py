from django import forms

from api.utils.forms import DeleteObjectForm
from app.models import Resource


class CreateUpdateResourceForm(forms.ModelForm):
    files = forms.FileField(
        widget=forms.FileInput(attrs={"multiple": True}), required=False  # type: ignore
    )

    class Meta:
        model = Resource
        fields = ("id", "title", "resource_type", "course", "date")


class DeleteResourceForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Resource
