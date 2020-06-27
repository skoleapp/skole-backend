from typing import Any, Dict, Optional

from django import forms

from skole.models import User
from skole.utils.constants import ValidationErrors
from skole.utils.shortcuts import validate_is_first_inherited
from skole.utils.types import ID


class TargetForm(forms.ModelForm):
    """A base class for forms that require a single object as a target.

    Should be the first class in the inheritance list.
    """

    def clean(self) -> Dict[str, Any]:
        """Ensure that the created object has exactly one foreign key it targets."""

        # Ignore: `clean` will be defined when this mixin is used.
        cleaned_data = super().clean()  # type: ignore[misc]

        targets: Dict[str, ID] = {
            "course": None,
            "comment": None,
            "resource": None,
            "vote": None,
        }

        for target in targets:
            targets[target] = cleaned_data.pop(target, None)

        target_list = [target for target in targets.values() if target is not None]

        if len(target_list) != 1:
            raise forms.ValidationError(ValidationErrors.MUTATION_INVALID_TARGET)

        cleaned_data["target"] = target_list[0]
        return cleaned_data

    def __init_subclass__(cls) -> None:
        validate_is_first_inherited(TargetForm, cls)
        super().__init_subclass__()


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
            raise forms.ValidationError(ValidationErrors.NOT_OWNER)

        self.cleaned_data["target"] = self.instance
        return self.cleaned_data
