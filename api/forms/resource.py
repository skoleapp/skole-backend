from django import forms

from api.utils.forms import DeleteObjectForm
from core.models import Resource


class CreateUpdateResourceForm(forms.ModelForm):
    file = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "accept": "application/pdf, application/msword, application/vnd.ms-excel, image/*"
            }
        )
    )

    class Meta:
        model = Resource
        fields = ("id", "title", "resource_type", "course", "date")


class DeleteResourceForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Resource
