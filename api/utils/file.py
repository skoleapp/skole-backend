from typing import Any

from graphql import ResolveInfo
from mypy.types import JsonDict


class FileMixin:
    """A mixin for passing the files of the request to the model form so the validation can be done there."""

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        assert info.context is not None
        return {
            "data": input,
            "instance": info.context.user,
            "files": info.context.FILES,
        }
