from typing import Dict, List, Optional, Type, TypeVar

from django import forms
from django.db import models
from django.utils.translation import gettext as _

from app.models import Comment, Resource, ResourcePart, Vote

T = TypeVar("T", bound=models.Model)


def get_obj_or_none(model: Type[T], obj_id: int) -> Optional[T]:
    """Used as a helper function to return None instead of raising a GraphQLError."""
    try:
        return model.objects.get(pk=obj_id)
    except model.DoesNotExist:
        return None


class TargetMixin:
    def clean(self) -> Dict[str, str]:
        """Ensure that the created object has exactly one foreign key it targets."""
        cleaned_data = self.cleaned_data  # type: ignore
        targets: Dict[str, Optional[int]] = {}

        targets["comment_id"] = cleaned_data.pop("comment_id", None)
        targets["resource_id"] = cleaned_data.pop("resource_id", None)
        targets["resource_part_id"] = cleaned_data.pop("resource_part_id", None)
        targets["vote_id"] = cleaned_data.pop("vote_id", None)

        if len([val for val in targets.values() if val is not None]) != 1:
            raise forms.ValidationError(_("Invalid mutation input."))

        if pk := targets["comment_id"] is not None:
            cleaned_data["target"] = Comment.objects.get(pk=pk)
        elif pk := targets["resource_id"] is not None:
            cleaned_data["target"] = Resource.objects.get(pk=pk)
        elif pk := targets["resource_part_id"] is not None:
            cleaned_data["target"] = ResourcePart.objects.get(pk=pk)
        elif pk := targets["vote_id"] is not None:
            cleaned_data["target"] = Vote.objects.get(pk=pk)
        else:
            raise AssertionError("Unexpected error.")  # Mutation target is null.

        return cleaned_data
