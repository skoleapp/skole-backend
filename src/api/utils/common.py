from typing import Dict, List, Optional, Type, TypeVar

from django import forms
from django.db import models
from django.utils.translation import gettext as _

T = TypeVar("T", bound=models.Model)


def get_obj_or_none(model: Type[T], obj_id: int) -> Optional[T]:
    """Used as a helper function to return None instead of raising a GraphQLError."""
    try:
        return model.objects.get(pk=obj_id)
    except model.DoesNotExist:
        return None


class TargetMixin:
    @staticmethod
    def invalid_mutation_input():
        raise forms.ValidationError(_("Invalid mutation input."))

    def clean(self) -> Dict[str, str]:
        """Ensure that the created object has exactly one foreign key it targets."""
        cleaned_data = self.cleaned_data
        targets: Dict[str, any] = {}

        targets["comment_id"] = cleaned_data.pop("comment_id", None)
        targets["resource_id"] = cleaned_data.pop("resource_id", None)
        targets["resource_part_id"] = cleaned_data.pop("resource_part_id", None)
        targets["vote_id"] = cleaned_data.pop("vote_id", None)

        if len(targets.values) != 1:
            self.invalid_mutation_input()

        if pk := targets["comment_id"] is not None:
            cleaned_data["target"] = Comment.objects.get(pk=pk)
        elif pk := targets["resource_id"] is not None:
            cleaned_data["target"] = Resource.objects.get(pk=pk)
        elif pk := targets["resource_part_id"] is not None:
            cleaned_data["target"] = ResourcePart.objects.get(pk=pk)
        elif pk := targets["vote_id"] is not None:
            cleaned_data["target"] = Vote.objects.get(pk=pk)
        else:
            self.invalid_mutation_input()

        return cleaned_data
