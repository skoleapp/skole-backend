from typing import cast

from skole.models import Starred
from skole.types import JsonDict, StarrableModel
from skole.utils.shortcuts import validate_single_target

from .base import SkoleModelForm


class CreateStarForm(SkoleModelForm):
    class Meta:
        model = Starred
        fields = ("course", "resource")

    def clean(self) -> JsonDict:
        data = super().clean()
        data["target"] = cast(
            StarrableModel, validate_single_target(data, "course", "resource")
        )
        return data
