from typing import Dict, List, Optional, Type, TypeVar, Union

from django import forms
from django.db import models
from django.utils.translation import gettext as _

from app.models import Comment, Course, Resource, ResourcePart, Vote

T = TypeVar("T", bound=models.Model)


def get_obj_or_none(model: Type[T], pk: int) -> Optional[T]:
    """Used as a helper function to return None instead of raising a GraphQLError."""
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None


class TargetForm(forms.ModelForm):
    comment_id = forms.IntegerField(required=False)
    course_id = forms.IntegerField(required=False)
    resource_id = forms.IntegerField(required=False)
    resource_part_id = forms.IntegerField(required=False)
    vote_id = forms.IntegerField(required=False)

    def get_target(
        self, targets: Dict[str, Optional[int]]
    ) -> Union[Course, Comment, Resource, ResourcePart, Vote, None]:
        if pk := targets.get("course_id"):
            return get_obj_or_none(Course, pk) # type: ignore[arg-type]
        elif pk := targets.get("comment_id"):
            return get_obj_or_none(Comment, pk) # type: ignore[arg-type]
        elif pk := targets.get("resource_id"):
            return get_obj_or_none(Resource, pk) # type: ignore[arg-type]
        elif pk := targets.get("resource_part_id"):
            return get_obj_or_none(ResourcePart, pk) # type: ignore[arg-type]
        elif pk := targets.get("vote_id"):
            return get_obj_or_none(Vote, pk) # type: ignore[arg-type]
        else:
            return None

    def clean(self) -> Dict[str, str]:
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

        # Ensure that the created object has exactly one foreign key it targets.
        if len([val for val in targets.values() if val is not None]) != 1:
            raise forms.ValidationError(_("Mutation contains too many targets!"))

        if target := self.get_target(targets):
            cleaned_data["target"] = target
        else:
            raise forms.ValidationError(
                _("Mutation must have at least one target object.")
            )

        return cleaned_data
