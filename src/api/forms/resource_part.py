from django import forms

from app.models import ResourcePart


class CreateResourcePartForm(forms.ModelForm):
    resource_id = forms.IntegerField()
    file = forms.FileField(
        widget=forms.FileInput(attrs={"multiple": False}), required=True  # type: ignore
    )

    class Meta:
        model = ResourcePart
        fields = ("resource_id", "resource_part_type", "title", "file")


class UpdateResourcePartForm(forms.ModelForm):
    resource_part_id = forms.IntegerField()
    file = forms.FileField(
        widget=forms.FileInput(attrs={"multiple": False}), required=True  # type: ignore
    )

    class Meta:
        model = ResourcePart
        fields = ("resource_part_id", "resource_part_type", "title", "file")
