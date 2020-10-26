from functools import wraps
from typing import Callable, Optional, TypeVar

from skole.models import User
from skole.types import ResolveInfo

T = TypeVar("T")
UserResolver = Callable[[User, ResolveInfo], T]


def private_field(func: UserResolver[T]) -> UserResolver[Optional[T]]:
    """Use as a decorator to only return the field's value if it's the user's own."""

    @wraps(func)
    def wrapper(root: User, info: ResolveInfo) -> Optional[T]:
        if info.context.user.is_authenticated and root.pk == info.context.user.pk:
            return func(root, info)
        else:
            return None

    return wrapper
