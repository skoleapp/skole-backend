from typing import Any, Dict, Optional

from django import forms
from django.http import HttpRequest

from skole.utils.constants import ValidationErrors


class _SkoleFormMixin:
    def __init__(self, *, request: Optional[HttpRequest] = None, **kwargs: Any) -> None:
        # `request` cannot be a required parameter since `DjangoModelFormMutation`
        # initializes all forms once without passing in any args.
        self.request = request
        files = kwargs.pop("files", None) or getattr(self.request, "FILES", None)
        # Ignore: `object` doesn't take these kwargs, but forms do.
        super().__init__(**kwargs, files=files)  # type: ignore[call-arg]


class SkoleForm(_SkoleFormMixin, forms.Form):
    """Base class for all plain forms."""


class SkoleModelForm(_SkoleFormMixin, forms.ModelForm):
    """Base class for all model forms."""


class SkoleUpdateModelForm(SkoleModelForm):
    """Base class for forms that are used for updating objects."""

    def clean(self) -> Dict[str, str]:
        data = super().clean()

        user = getattr(self.request, "user", None)
        if not user or self.instance.user != user:
            raise forms.ValidationError(ValidationErrors.NOT_OWNER)

        return data
