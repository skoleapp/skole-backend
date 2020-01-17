from django import forms

from app.models import Resource


class UploadResourceForm(forms.ModelForm):
    files = forms.FileField(
        widget=forms.FileInput(attrs={"multiple": True}), required=False
    )

    class Meta:
        model = Resource
        fields = ("title", "resource_type", "course")
