from typing import Any, Dict, Optional

from django import forms
from django.utils.translation import gettext as _

from api.utils.messages import NOT_OWNER_MESSAGE
from core.models import User


class TargetForm(forms.ModelForm):
    """A base class for forms that require a single object as a target."""

    def clean(self) -> Dict[str, str]:
        """Ensure that the created object has exactly one foreign key it targets."""
        cleaned_data = self.cleaned_data

        targets: Dict[str, Optional[int]] = {
            "course": None,
            "comment": None,
            "resource": None,
            "vote": None,
        }

        for target in targets:
            targets[target] = cleaned_data.pop(target, None)

        target_list = [target for target in targets.values() if target is not None]

        if len(target_list) != 1:
            raise forms.ValidationError(_("Mutation needs exactly one target."))

        cleaned_data["target"] = target_list[0]
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
            raise forms.ValidationError(NOT_OWNER_MESSAGE)

        self.cleaned_data["target"] = self.instance
        return self.cleaned_data
