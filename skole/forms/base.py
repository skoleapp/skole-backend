from typing import Any, Dict, Optional

from django import forms
from django.http import HttpRequest

from skole.utils.constants import ValidationErrors


class SkoleModelForm(forms.ModelForm):
    """Base class for all model forms."""

    def __init__(self, **kwargs: Any) -> None:
        # Cannot be a required parameter since DjangoModelFormMutation
        # initializes all forms once without passing in any args.
        self.request: Optional[HttpRequest] = kwargs.pop("request", None)
        files = kwargs.pop("files", None) or getattr(self.request, "FILES", None)
        # Ignore: Mypy thinks that super can get multiple values for `files`, even
        #  though it's popped away from kwargs.
        super().__init__(**kwargs, files=files)  # type: ignore[misc]


class SkoleUpdateModelForm(SkoleModelForm):
    """Base class for forms that are used for updating objects."""

    def clean(self) -> Dict[str, str]:
        data = super().clean()

        user = getattr(self.request, "user", None)
        if not user or self.instance.user != user:
            raise forms.ValidationError(ValidationErrors.NOT_OWNER)

        return data
