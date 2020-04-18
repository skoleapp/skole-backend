from typing import Any

from graphql import ResolveInfo
from mypy.types import JsonDict


class FileMixin:
    """A mixin for passing the files of the request to the model form
    so that he validation can be done there.
    """

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        assert info.context is not None

        # Ignore: get_form_kwargs will exist in the super class when this mixin is used
        #   together with a DjangoModelFormMutation.
        form_kwargs = super().get_form_kwargs(root, info, **input)  # type: ignore[misc]
        form_kwargs["files"] = info.context.FILES
        if info.context.user:
            form_kwargs["instance"] = info.context.user
        return form_kwargs
