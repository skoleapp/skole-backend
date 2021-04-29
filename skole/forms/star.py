from __future__ import annotations

from skole.forms.base import SkoleModelForm
from skole.models import Star


class CreateStarForm(SkoleModelForm):
    class Meta:
        model = Star
        fields = ("thread",)
