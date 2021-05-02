from __future__ import annotations

from skole.types import FormError


def to_form_error(value: str) -> FormError:
    """Use to add the GraphQL mutation form error structure to an error message."""
    return [{"field": "__all__", "messages": [value]}]
