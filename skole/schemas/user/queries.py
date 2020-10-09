from typing import Optional

import graphene
from django.contrib.auth import get_user_model
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required

from skole.models import User
from skole.types import ID

from .object_types import UserObjectType


class Query(graphene.ObjectType):

    user = graphene.Field(UserObjectType, id=graphene.ID())
    user_me = graphene.Field(UserObjectType)

    def resolve_user(self, info: ResolveInfo, id: ID = None) -> Optional[User]:
        try:
            # Ignore: Mypy complains that `get(pk=None)` is not valid. It might not be
            #  the most sensible thing, but it actually doesn't fail at runtime.
            return get_user_model().objects.filter(is_superuser=False).get(pk=id)  # type: ignore[misc]
        except User.DoesNotExist:
            return None

    @login_required
    def resolve_user_me(self, info: ResolveInfo) -> User:
        assert info.context is not None
        return info.context.user
