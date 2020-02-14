from typing import Dict, Optional, Type, TypeVar

from django import forms
from django.db import models
from django.utils.translation import gettext as _

T = TypeVar("T", bound=models.Model)


def get_obj_or_none(model: Type[T], pk: int) -> Optional[T]:
    """Used as a helper function to return None instead of raising a GraphQLError."""
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None


class TargetForm(forms.ModelForm):
    def clean(self) -> Dict[str, str]:
        """Ensure that the created object has exactly one foreign key it targets."""
        cleaned_data = self.cleaned_data

        targets: Dict[str, Optional[int]] = {
            "course": None,
            "comment": None,
            "resource": None,
            "resource_part": None,
            "vote": None,
        }

        for i in targets.keys():
            targets[i] = cleaned_data.pop(i, None)

        if len([val for val in targets.values() if val is not None]) != 1:
            raise forms.ValidationError(_("Mutation contains too many targets!"))

        return cleaned_data
