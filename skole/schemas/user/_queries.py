from typing import Optional, cast

import graphene
from django.contrib.auth import get_user_model

from skole.models import User
from skole.overridden import login_required
from skole.schemas.base import SkoleObjectType
from skole.types import ID, ResolveInfo

from ._object_types import UserObjectType


class Query(SkoleObjectType):
    user_me = graphene.Field(UserObjectType)

    user = graphene.Field(UserObjectType, id=graphene.ID())

    @staticmethod
    @login_required
    def resolve_user_me(root: None, info: ResolveInfo) -> User:
        """Return user profile of the user making the query."""
        return cast(User, info.context.user)

    @staticmethod
    def resolve_user(root: None, info: ResolveInfo, id: ID = None) -> Optional[User]:
        """Superusers cannot be queried."""
        try:
            # Ignore: Mypy complains that `get(pk=None)` is not valid.
            # It might not be the most sensible thing, but it actually doesn't fail at runtime.
            return get_user_model().objects.filter(is_superuser=False).get(pk=id)  # type: ignore[misc]
        except User.DoesNotExist:
            return None
