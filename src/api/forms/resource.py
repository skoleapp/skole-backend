from django import forms

from app.models import Resource


class CreateResourceForm(forms.ModelForm):
    files = forms.FileField(
        widget=forms.FileInput(attrs={"multiple": True}), required=False  # type: ignore
    )

    class Meta:
        model = Resource
        fields = ("title", "resource_type", "course", "date")


class UpdateResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ("id", "title", "resource_type", "date")
