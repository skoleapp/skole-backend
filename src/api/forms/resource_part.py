from django import forms

from app.models import ResourcePart


class CreateResourcePartForm(forms.ModelForm):
    file = forms.FileField(
        widget=forms.FileInput(attrs={"multiple": False}), required=True  # type: ignore
    )

    class Meta:
        model = ResourcePart
        fields = ("resource", "resource_part_type", "title", "file")


class UpdateResourcePartForm(forms.ModelForm):
    file = forms.FileField(
        widget=forms.FileInput(attrs={"multiple": False}), required=True  # type: ignore
    )

    class Meta:
        model = ResourcePart
        fields = ("id", "resource_part_type", "title", "file")
