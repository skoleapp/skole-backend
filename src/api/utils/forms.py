from typing import Any, Dict, Optional

from django import forms
from django.utils.translation import gettext as _

from app.models import User


class TargetForm(forms.ModelForm):
    "A base class for forms that require a single object as a target."

    def clean(self) -> Dict[str, str]:
        """Ensure that the created object has exactly one foreign key it targets."""
        cleaned_data = self.cleaned_data

        targets: Dict[str, Optional[int]] = {
            "course": None,
            "comment": None,
            "resource": None,
            "resource_file": None,
            "vote": None,
        }

        for i in targets.keys():
            targets[i] = cleaned_data.pop(i, None)

        if len([val for val in targets.values() if val is not None]) != 1:
            raise forms.ValidationError(_("Mutation contains too many targets!"))

        # Place first not None item from targets dict as the cleaned target.
        cleaned_data["target"] = next(
            target for target in targets.values() if target is not None
        )
        return cleaned_data


class DeleteObjectForm(forms.ModelForm):
    """Base class for forms that are used for deleting single objects."""

    class Meta:
        fields = ("id",)

    def __init__(self, user: Optional[User] = None, **kwargs: Any) -> None:
        if user is not None:
            self.user = user

        super().__init__(**kwargs)

    def clean(self) -> Dict[str, str]:
        if self.instance.user != self.user:
            raise forms.ValidationError(_("You are not the owner of this object!"))

        self.cleaned_data["target"] = self.instance
        return self.cleaned_data
