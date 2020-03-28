from typing import Optional

import graphene
from graphql import ResolveInfo

from core.models import Course, Resource, Starred


class StarredMixin:
    starred = graphene.Boolean()

    def resolve_starred(self, info: ResolveInfo) -> Optional[int]:
        """Check whether user has starred current item."""

        user = info.context.user

        if user.is_anonymous:
            return False

        try:
            if isinstance(self, Course):
                # Ignore: pk attribute will be defined in the class deriving from this mixin.
                return user.stars.get(course=self.pk) is not None  # type: ignore [attr-defined]
            if isinstance(self, Resource):
                # Ignore: pk attribute will be defined in the class deriving from this mixin.
                return user.stars.get(resource=self.pk) is not None  # type: ignore [attr-defined]
            else:
                raise TypeError("Invalid class.")

        except Starred.DoesNotExist:
            return False
