from django import forms

from app.models import Resource


class UploadResourceForm(forms.ModelForm):
    resource_type_id = forms.IntegerField()
    course_id = forms.IntegerField()
    files = forms.FileField(
        widget=forms.FileInput(attrs={"multiple": True}), required=False  # type: ignore
    )

    class Meta:
        model = Resource
        fields = ("title", "resource_type_id", "course_id", "date")


class UpdateResourceForm(forms.ModelForm):
    resource_id = forms.IntegerField()
    resource_type_id = forms.IntegerField()

    class Meta:
        model = Resource
        fields = ("resource_id", "title", "resource_type_id", "date")
