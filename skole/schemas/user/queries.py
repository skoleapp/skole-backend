from typing import Optional, cast

import graphene
from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required

from skole.models import User
from skole.types import ID, ResolveInfo
from skole.utils import api_descriptions

from .object_types import UserObjectType


class Query(graphene.ObjectType):
    user_me = graphene.Field(UserObjectType, description=api_descriptions.USER_ME)

    user = graphene.Field(
        UserObjectType, id=graphene.ID(), description=api_descriptions.USER
    )

    @staticmethod
    @login_required
    def resolve_user_me(root: None, info: ResolveInfo) -> User:
        return cast(User, info.context.user)

    @staticmethod
    def resolve_user(root: None, info: ResolveInfo, id: ID = None) -> Optional[User]:
        try:
            # Ignore: Mypy complains that `get(pk=None)` is not valid.
            # It might not be the most sensible thing, but it actually doesn't fail at runtime.
            return get_user_model().objects.filter(is_superuser=False).get(pk=id)  # type: ignore[misc]
        except User.DoesNotExist:
            return None
