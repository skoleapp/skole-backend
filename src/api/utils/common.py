from typing import Dict, List, Optional, Type, TypeVar

from django import forms
from django.db import models
from django.utils.translation import gettext as _

T = TypeVar("T", bound=models.Model)


def get_obj_or_none(model: Type[T], obj_id: int) -> Optional[T]:
    try:
        return model.objects.get(pk=obj_id)
    except model.DoesNotExist:
        return None


def clean_target(cleaned_data: Dict[str, str], *args: str) -> Dict[str, str]:
    """Ensure that the created object has exactly one foreign key it targets."""
    targets: List[Optional[str]] = []

    for i in args:
        targets.append(cleaned_data.pop(i, None))

    target = [n for n in targets if n is not None]

    if len(target) != 1:
        raise forms.ValidationError(_("Mutation input contains incorrect target."))

    cleaned_data["target"] = target[0]
    return cleaned_data
