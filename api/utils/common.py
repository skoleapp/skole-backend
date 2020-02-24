from typing import Optional, Type, TypeVar

from django.db import models

T = TypeVar("T", bound=models.Model)


def get_obj_or_none(model: Type[T], pk: Optional[int] = None) -> Optional[T]:
    """Used as a helper function to return None instead of raising a GraphQLError."""
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None
