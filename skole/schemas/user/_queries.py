from typing import Optional, cast

import graphene
from django.contrib.auth import get_user_model

from skole.models import User
from skole.overridden import login_required
from skole.schemas.base import SkoleObjectType
from skole.schemas.user import UserObjectType
from skole.types import ResolveInfo


class Query(SkoleObjectType):
    user_me = graphene.Field(UserObjectType)
    user = graphene.Field(UserObjectType, slug=graphene.String())

    @staticmethod
    @login_required
    def resolve_user_me(root: None, info: ResolveInfo) -> User:
        """Return user profile of the user making the query."""
        return cast(User, info.context.user)

    @staticmethod
    def resolve_user(root: None, info: ResolveInfo, slug: str = "") -> Optional[User]:
        """Superusers cannot be queried."""
        try:
            return get_user_model().objects.filter(is_superuser=False).get(slug=slug)
        except User.DoesNotExist:
            return None
