from django import forms

from api.utils.forms import DeleteObjectForm
from core.models import Resource


class CreateUpdateResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ("id", "title", "file", "resource_type", "course", "date")

    def clean_file(self) -> str:
        # Ignore: Mypy considers files as optional but they're always at least an empty MultiValueDict.
        if file := self.files.get("1", None):  # type: ignore [union-attr]
            return file
        else:
            return self.cleaned_data["file"]


class DeleteResourceForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Resource
