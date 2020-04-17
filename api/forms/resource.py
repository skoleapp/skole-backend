from django import forms

from api.utils.forms import DeleteObjectForm
from core.models import Resource


class CreateResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ("title", "file", "resource_type", "course", "date")

    def clean_file(self) -> str:
        # Ignore: Mypy considers files as optional but they're always at least an empty MultiValueDict.
        if file := self.files.get("1", None):  # type: ignore [union-attr]
            return file
        else:
            return self.cleaned_data["file"]


class UpdateResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ("title", "resource_type", "date")

    clean_file = CreateResourceForm.clean_file


class DeleteResourceForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Resource
