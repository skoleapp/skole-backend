from typing import cast

from skole.forms.base import SkoleModelForm
from skole.models import Star
from skole.types import JsonDict, StarrableModel
from skole.utils.validators import validate_single_target


class CreateStarForm(SkoleModelForm):
    class Meta:
        model = Star
        fields = ("course", "resource")

    def clean(self) -> JsonDict:
        data = super().clean()
        data["target"] = cast(
            StarrableModel, validate_single_target(data, "course", "resource")
        )

        return data
