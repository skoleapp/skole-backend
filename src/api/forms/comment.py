from django import forms
from mypy.types import JsonDict

from api.utils.messages import INCORRECT_TARGET_FOR_COMMENT_MESSAGE
from app.models import Comment


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text", "attachment", "course", "resource", "resource_part")

    def clean(self) -> JsonDict:
        """Ensure that any created comment has exactly one foreign key it targets."""
        course = self.cleaned_data.pop("course", None)
        resource = self.cleaned_data.pop("resource", None)
        resource_part = self.cleaned_data.pop("resource_part", None)

        target = [n for n in (course, resource, resource_part) if n is not None]
        if len(target) != 1:
            raise forms.ValidationError(INCORRECT_TARGET_FOR_COMMENT_MESSAGE)

        self.cleaned_data["target"] = target[0]
        return self.cleaned_data
