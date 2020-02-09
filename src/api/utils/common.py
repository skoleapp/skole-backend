from typing import Dict, List, Optional, Type, TypeVar, Union

from django import forms
from django.db import models
from django.utils.translation import gettext as _

from app.models import Comment, Course, Resource, ResourcePart, Vote

T = TypeVar("T", bound=models.Model)


def get_obj_or_none(model: Type[T], obj_id: int) -> Optional[T]:
    """Used as a helper function to return None instead of raising a GraphQLError."""
    try:
        return model.objects.get(pk=obj_id)
    except model.DoesNotExist:
        return None


class TargetForm(forms.ModelForm):
    @staticmethod
    def get_target(targets: Dict[str, Optional[int]]) -> Union[Course, Comment, Resource, ResourcePart, Vote]:
        if pk := targets["course_id"] is not None:
            return Course.objects.get(pk=pk)
        elif pk := targets["comment_id"] is not None:
            return Comment.objects.get(pk=pk)
        elif pk := targets["resource_id"] is not None:
            return Resource.objects.get(pk=pk)
        elif pk := targets["resource_part_id"] is not None:
            return ResourcePart.objects.get(pk=pk)
        elif pk := targets["vote_id"] is not None:
            return Vote.objects.get(pk=pk)
        else:
            raise AssertionError("Unexpected error.")  # Mutation target is null.

    def clean(self) -> Dict[str, str]:
        """Ensure that the created object has exactly one foreign key it targets."""
        cleaned_data = self.cleaned_data

        targets: Dict[str, Optional[int]] = {
            "course_id": None,
            "comment_id": None,
            "resource_id": None,
            "resource_part_id": None,
            "vote_id": None,
        }

        for i in targets.keys():
            targets[i] = cleaned_data.pop(i, None)

        if len([val for val in targets.values() if val is not None]) != 1:
            raise forms.ValidationError(_("Invalid mutation input."))

        cleaned_data["target"] = self.get_target(targets)
        return cleaned_data
